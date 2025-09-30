import whisper
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY
import os

# File in cui sono presenti i modelli per lo speech-to-text e per la correzione delle trascrizioni

# Caricamento modello Whisper una sola volta
MODEL_NAME = "base"

# Impostazione delle credenziali Google Cloud
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
 

def load_model_stt(): # modello per lo speech-to-text
    return whisper.load_model(MODEL_NAME)


def load_model_correction(): # modello per la correzione delle trascrizioni
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash")
