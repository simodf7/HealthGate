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

# Percorso della cartella
cartella = "../documents"

documents = []

# Elenco dei file con il loro percorso completo
for pdf_path in os.listdir(cartella):
    loader = PyPDFLoader(pdf_path)
    documents.extend(loader.load())

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
docs_official = splitter.split_documents(documents)

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
client = chromadb.HttpClient(host="localhost", port=8000, ssl=False)

vector_store_from_client = Chroma(
    client=client,
    collection_name="collection_name",
    embedding_function=embeddings,
)

uuids = [str(uuid4()) for _ in range(len(documents))]

vector_store_from_client.add_documents(documents=docs_official, ids=uuids)


retriever_official = vector_store_from_client.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4, "filter": {"fonte": "Ministero della Salute"}}
)


# ========================================
# 2️⃣ --- Caricamento report del paziente (da MongoDB) ---
# ========================================
'''

def get_patient_reports(codice_paziente: str):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["healthcare"]
    collection = db["reports"]
    return list(collection.find({"codice_paziente": codice_paziente}))

codice_paziente = "PZ00123"
reports = get_patient_reports(codice_paziente)

docs_patient = []
for r in reports:
    testo = r.get("testo_completo", "")
    if testo:
        docs_patient.append(
            Document(
                page_content=testo,
                metadata={
                    "fonte": "report_paziente",
                    "id_report": str(r["_id"]),
                    "data": str(r.get("data_creazione")),
                },
            )
        )

if docs_patient:
    vectorstore_patient = Chroma.from_documents(
        docs_patient,
        embedding=embeddings,
        persist_directory=f"./db_vect_patient/{codice_paziente}"
    )
    retriever_patient = vectorstore_patient.as_retriever(search_type="similarity", search_kwargs={"k": 3})
else:
    retriever_patient = None
''' 

# ========================================
# 3️⃣ --- Creazione retriever combinato ---
# ========================================

''' 
if retriever_patient:
    retriever = MergerRetriever(retrievers=[retriever_official, retriever_patient])
else:
    retriever = retriever_official  # fallback se non ci sono report precedenti
''' 


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

risultato = rag_chain.invoke({
    "input": "Analizza la necessità di pronto soccorso",
    "storia_paziente": storia,
    "sintomi": sintomi
})
 
# 8️⃣ --- Output finale ---

print("🧾 Risposta JSON:")

print(risultato["answer"])
 
print("\n📚 Fonti utilizzate:")

for doc in risultato["context"]:

    print("-", doc.metadata.get("fonte"), "|", doc.metadata.get("id_report", doc.metadata.get("tipo")))



