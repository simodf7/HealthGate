from dotenv import load_dotenv
import os

# Carica il file .env
load_dotenv()

# Recupera le variabili
AUDIO_FOLDER = os.getenv("AUDIO_FOLDER")
TRANSCRIPTS_FOLDER = os.getenv("TRANSCRIPTS_FOLDER")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")