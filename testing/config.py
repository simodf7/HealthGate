from dotenv import load_dotenv
import os

# Carica il file .env
load_dotenv()

# Recupera le variabili
API_KEY = os.getenv("API_KEY")
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = os.getenv("CHROMA_PORT")
