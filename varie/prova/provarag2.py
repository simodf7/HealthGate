import getpass
import os

from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import chromadb
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate

from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
import re



# Impostazione delle credenziali Google Cloud


if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")


llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
 ## valutare se cambiare con all-mpnet-base-v2, piu accurato ma piu lento 
# abhinand/MedEmbed-small-v0.1"


client = chromadb.HttpClient(host="localhost", port=8000, ssl=False)
vector_store = Chroma(
    client=client,
    collection_name="collection_name",
    embedding_function=embeddings,
)


def clean_text(text: str) -> str:
    # Rimuovere soft hyphen
    text = re.sub(r"\xad", "", text)
    
    # 2. Rimuove newline interni (multi-colonna), salvo punteggiatura forte o titoli/elenco
    text = re.sub(r"(?<![.!?:;])\n(?!\s*[A-Z0-9□■])", "", text)

    # 3. Riduce spazi multipli
    text = re.sub(r"\s{2,}", " ", text)

    # 4. Corregge spazi strani con apostrofo (d ’ → d’)
    text = re.sub(r"\s’", r"’", text)

    text = re.sub(r'(?<=[a-zà-ú0-9])\.(?=[A-ZÀ-Ýa-zà-ú])', ". ", text)


    # Rimuovere underscore multipli
    text = re.sub(r"_+", "", text)

    # Uniformare i line break tra paragrafi
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    text = re.sub(r"([’'])\s+", r"\1", text)

    # Rimuove trattino seguito da spazio o newline e ricompone la parola
    text = re.sub(r"-\s+", "", text)

    # 🔹 Ricompone parole spezzate da sillabazione
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    text = re.sub(r"[■][^\n,.;:]*", "", text)

    text = re.sub(
        r'^[ \t]*[□]\s*(.+?)(?:\r?\n|$)',
        lambda m: m.group(1).strip() + (". "),
        text,
        flags=re.MULTILINE
    )

    
    text = re.sub(r'^[A-ZÀÖØÞ]{2,}(?:\s+[A-ZÀÖØÞ]{2,})*', '', text, flags=re.MULTILINE)

    return text


'''
# Percorso assoluto della cartella dove sono i PDF
base_dir = os.path.dirname(os.path.abspath(__file__))
cartella = os.path.abspath(os.path.join(base_dir, "..", "documents"))


# Scansiona la cartella e carica solo i PDF
for filename in os.listdir(cartella):
    txt_path = os.path.join(cartella, filename)   # QUI costruisci il path completo
    if os.path.isfile(txt_path) and filename.lower().endswith(".txt"):
        print(f"Carico: {txt_path}")  # debug per verificare il percorso
        loader = TextLoader(txt_path, encoding="utf-8")
        docs = loader.load()
    
"""
for doc in docs:
    doc.page_content = clean_text(doc.page_content)
"""

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
all_splits = splitter.split_documents(docs)


# Index chunks
_ = vector_store.add_documents(documents=all_splits)
'''

prompt_template = """
    Sei un assistente sanitario virtuale.

    Un paziente ti fornisce informazioni sui suoi sintomi. 
    Riceverai inoltre informazioni da un Retriever che ha accesso a linee guida ospedialiere ufficiali.
    Inoltre sempre il retriever ti fornirà uno storico clinico del paziente, se presente.
    
    IMPORTANTE:
    - Le tue decisioni devono basarsi **esclusivamente** sui documenti forniti dal Retriever.
    - Non utilizzare conoscenze esterne o supposizioni personali.
    
    Il tuo compito è il seguente: 
    - Classificare se il paziente deve recarsi al pronto soccorso immediatamente o se non è necessario.
    - Fornire una motivazione concisa basata sui documenti forniti.
    
    L'input che ricevi è strutturato come segue:

    Sintomi del paziente: {sintomi}

    Storia clinica del paziente: {storia_paziente}
    
    Estatti da linee guida ufficiali relativi ai sintomi: {context}

    Rispondi seguendo ESATTAMENTE con la struttura seguente in formato JSON.
    
    Answer: 
    {{
        "decisione": "Pronto soccorso necessario" o "Pronto soccorso non necessario",
        "motivazione": "Breve spiegazione della decisione"
    }}

"""




prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["sintomi", "storia_paziente", "context"]
)




# Define state for application
class State(TypedDict):
    sintomi: str
    storia_paziente: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["sintomi"] + state['storia_paziente'], k=6)
    print("\n\n--- RETRIEVED DOCS ---\n\n")
    for doc in retrieved_docs:
        print("Content: " +  doc.page_content + "\n")
        print("Source: " + doc.metadata['source'] + "\n")
        print("------------------------------------- + \n")


    return {"context": retrieved_docs}


def generate(state: State):
    #print("\n\n--- STATE ---\n\n")
    #print("context: ", state['context'])
    #print("sintomi: ", state['sintomi'])
    #print("storia_paziente: ", state['storia_paziente'])

    #print("\n\n-----\n\n")

    docs_content = "\n\n".join("'" + doc.page_content + "'" for doc in state["context"])

    print("\n\n--- DOCS CONTENT ---\n\n")
    print(docs_content)
    print("\n\n-----\n\n")


    messages = prompt.invoke({"sintomi": state["sintomi"], "storia_paziente": state["storia_paziente"], "context": docs_content})
    response = llm.invoke(messages, temperature=0)
    return {"answer": response.content}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


# ESEMPIO 

storia = """Donna di 45 anni, in precedenza sana."""

sintomi = """Da due giorni febbre fino a 38,5 °C con brividi e malessere generale.
Tosse produttiva con catarro giallastro e dolore toracico in inspirazione profonda.
Riferisce lieve difficoltà respiratoria durante gli sforzi.
"""


response = graph.invoke({"sintomi": sintomi, "storia_paziente": storia})
print(response["answer"])
