# =============================
# FASE 2 - Decisione Pronto Soccorso (RAG) con PostgreSQL + MongoDB
# =============================

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.retrievers import MergerRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from uuid import uuid4
from langchain_core.documents import Document
from pymongo import MongoClient
import chromadb
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# ========================================
# 1️⃣ --- Caricamento documenti ufficiali ---
# ========================================

import os

# Impostazione delle credenziali Google Cloud
os.environ["GOOGLE_API_KEY"] = "AIzaSyALV5oqYTmoNAJ0S3H1q0Lw9YryWbN0qCo"
 

# Percorso assoluto della cartella dove sono i PDF
base_dir = os.path.dirname(os.path.abspath(__file__))
cartella = os.path.abspath(os.path.join(base_dir, "..", "documents"))

documents = []

# Scansiona la cartella e carica solo i PDF
for filename in os.listdir(cartella):
    pdf_path = os.path.join(cartella, filename)   # QUI costruisci il path completo
    if os.path.isfile(pdf_path) and filename.lower().endswith(".pdf"):
        print(f"Carico: {pdf_path}")  # debug per verificare il percorso
        loader = PyPDFLoader(pdf_path)
        documents.extend(loader.load())



for d in documents:
    d.metadata["fonte"] = filename
           
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
docs_official = splitter.split_documents(documents)


# embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
client = chromadb.HttpClient(host="localhost", port=8000, ssl=False)

vector_store_from_client = Chroma(
    client=client,
    collection_name="collection_name",
    embedding_function=embeddings,
)

uuids = [str(uuid4()) for _ in range(len(docs_official))]

vector_store_from_client.add_documents(documents=docs_official, ids=uuids)


retriever_official = vector_store_from_client.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4 }
)



# ========================================
# 4️⃣ --- Prompt personalizzato aggiornato ---
# ========================================
prompt_template = """
Sei un assistente sanitario virtuale.

Ricevi le seguenti informazioni:

📘 Estratti da linee guida ufficiali:
{context}

📄 Storico clinico del paziente (riassunto dai report precedenti, se presenti):
{storia_paziente}

🩺 Sintomi attuali:
{sintomi}

Analizza i dati e stabilisci se è necessario recarsi al pronto soccorso.
Devi basarti **solo** sui documenti forniti (ufficiali e personali) e restituire un JSON nel formato:

{{
  "classificazione": "andare_pronto_soccorso" | "non_necessario",
  "motivazione": "<spiega la decisione in modo conciso, basata sui documenti>",
  "fonti": ["id o titolo documento 1", "id o titolo documento 2"]
}}

Non aggiungere altro testo fuori dal JSON.
"""

PROMPT = PromptTemplate(
    input_variables=["storia_paziente", "sintomi", "context"],
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
Analizza la necessità di pronto soccorso per il seguente caso clinico.
Storia del paziente: {storia}
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

for doc in risultato["context"]:
    source = doc.metadata.get("title") or os.path.basename(doc.metadata.get("source", ""))
    page = doc.metadata.get("page")
    text = doc.page_content[:500] + "..."  # tronco per leggibilità (500 char)
    fonti_dettagliate.append({
        "titolo": source,
        "pagina": page,
        "contenuto": text
    })
 
import json

print(json.dumps(fonti_dettagliate, indent=2, ensure_ascii=False))

 

    

