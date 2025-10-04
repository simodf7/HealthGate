import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import whisper
from langchain_google_genai import ChatGoogleGenerativeAI
from config import API_KEY
import os

# File in cui sono presenti i modelli per embedding e llm
# e anche il vector store utilizzato



# Impostazione delle credenziali Google Cloud
os.environ["GOOGLE_API_KEY"] = API_KEY
 

def load_embedding_model(): # modello per lo speech-to-text
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def load_llm(): # modello per la correzione delle trascrizioni
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash")


def load_vector_store(embedding_model, port:8010):
    client = chromadb.HttpClient(host="localhost", port=port, ssl=False)
    return Chroma(
        client=client,
        collection_name="healthgate",
        embedding_function=embedding_model,
    )
