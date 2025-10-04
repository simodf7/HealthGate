# =============================
# FASE 2 - Decisione Pronto Soccorso (RAG) con PostgreSQL + MongoDB
# =============================

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
#from langchain.retrievers import MergerRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from uuid import uuid4
# from langchain_core.documents import Document
# from pymongo import MongoClient
import chromadb
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# ========================================
# 1️⃣ --- Caricamento documenti ufficiali ---
# ========================================

import os
import re


# Impostazione delle credenziali Google Cloud
os.environ["GOOGLE_API_KEY"] = "AIzaSyBuxrY6tmzNZhxxZxZKIjlsI2GBEwXpWMo"
 



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

# Percorso assoluto della cartella dove sono i PDF
base_dir = os.path.dirname(os.path.abspath(__file__))
cartella = os.path.abspath(os.path.join(base_dir, "..", "documents"))

total_documents = []



# Scansiona la cartella e carica solo i PDF
for filename in os.listdir(cartella):
    pdf_path = os.path.join(cartella, filename)   # QUI costruisci il path completo
    if os.path.isfile(pdf_path) and filename.lower().endswith(".pdf"):
        print(f"Carico: {pdf_path}")  # debug per verificare il percorso
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        for d in docs:
            d.metadata["source"] = filename
            d.page_content = clean_text(d.page_content)

        total_documents.extend(docs)



splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
chunks = splitter.split_documents(total_documents)


embeddings = HuggingFaceEmbeddings(model_name="abhinand/MedEmbed-small-v0.1")
client = chromadb.HttpClient(host="localhost", port=8000, ssl=False)

vector_store_from_client = Chroma(
    client=client,
    collection_name="collection_name",
    embedding_function=embeddings,
)

uuids = [str(uuid4()) for _ in range(len(chunks))]

vector_store_from_client.add_documents(documents=chunks, ids=uuids)


retriever_official = vector_store_from_client.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4 }
)



# ========================================
# 4️⃣ --- Prompt personalizzato aggiornato ---
# ========================================


prompt_template = """
    Sei un assistente sanitario virtuale.
    Un paziente ti fornisce informazioni sui suoi sintomi. 
    Riceverai inoltre informazioni da un Retriever che ha accesso a linee guida ospedialiere ufficiali.
    Inoltre sempre il retriever ti fornirà uno storico clinico del paziente, se presente.
    
    Il tuo compito è il seguente: 
    - Classificare se il paziente deve recarsi al pronto soccorso immediatamente o se non è necessario.
    - Fornire una motivazione concisa basata sui documenti forniti.
    - Elencare le fonti (documenti) che hai utilizzato per prendere la decisione.
    
    L'input che ricevi è strutturato come segue:

    Sintomi del paziente:
    {sintomi}

    Storia clinica del paziente:
    {storia_paziente}
    
    Estatti da linee guida ufficiali relativi ai sintomi:
    {context}

    Rispondi in formato JSON con i seguenti campi:
    {{
        "decisione": "Pronto soccorso necessario" o "Pronto soccorso non necessario",
        "motivazione": "Breve spiegazione della decisione basata sui documenti",
        "fonti": ["Titolo documento 1", "Titolo documento 2", ...]
    }}

    è imperativo che tu segua esattamente questo formato JSON.

"""

PROMPT = PromptTemplate(
    input_variables=["sintomi", "storia_paziente", "context"],
    template=prompt_template
)

# ========================================
# 5️⃣ --- Creazione della chain RAG ---
# ========================================

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# 5️⃣ --- Creazione della chain RAG (nuovo stile) ---

document_chain = create_stuff_documents_chain(llm, PROMPT)
rag_chain = create_retrieval_chain(retriever_official, document_chain)
 
# ========================================
# 6️⃣ --- Esempio di input ---
# ========================================

storia = """
    Il paziente è un uomo di 68 anni, iperteso, con diabete di tipo 2 e storia di angina stabile.
    Nessuna recente ospedalizzazione, in terapia con ACE inibitori e metformina.
"""

sintomi = """
    Da stamattina dolore toracico lieve, non irradiato, associato a leggero affanno e sudorazione.
"""

# 7️⃣ --- Esecuzione del sistema RAG ---

query = f"""
    Storia clinica: {storia}
    Sintomi: {sintomi}
"""

risultato = rag_chain.invoke({
    "input": query,
    "storia_paziente": storia,
    "sintomi": sintomi
})

 
# 8️⃣ --- Output finale ---

# Estrazione fonti dettagliate (titolo, pagina, testo)

print("Answer: ", risultato["answer"])

fonti_dettagliate = []
fonti = [doc for doc in risultato["context"]]
print(len(fonti))

for doc in fonti:
    source = doc.metadata.get("title") or os.path.basename(doc.metadata.get("source", ""))
    page = doc.metadata.get("page")
    text = doc.page_content
    fonti_dettagliate.append({
        "titolo": source,
        "pagina": page,
        "contenuto": text
    })
 
import json

print(json.dumps(fonti_dettagliate, indent=2, ensure_ascii=False))

 

    

