import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

from config import CHROMA_HOST, CHROMA_PORT

cartella = "documents"

docs = []

for filename in os.listdir(cartella):
    txt_path = os.path.join(cartella, filename)
    if os.path.isfile(txt_path) and filename.lower().endswith(".txt"):
        print(f"Carico: {txt_path}")
        loader = TextLoader(txt_path, encoding="utf-8")
        docs.extend(loader.load())

print(f"\nTotale documenti caricati: {len(docs)}")

# === ✂️ Suddivisione in chunk ===
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
chunks = splitter.split_documents(docs)
print(f"Totale chunk creati: {len(chunks)}")

# === 🧠 Embeddings e Chroma Client ===
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 🔗 Se il tuo Chroma è in container:
# usa host="chroma" (nome del servizio nel docker-compose)
client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT, ssl=False)

vector_store_from_client = Chroma(
    client=client,
    collection_name="collection_name",
    embedding_function=embeddings,
)

vector_store_from_client.add_documents(documents=chunks)

print(f"\n✅ Indicizzazione completata: {len(chunks)} chunk aggiunti a Chroma!")
