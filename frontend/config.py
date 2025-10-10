from dotenv import load_dotenv
import os

# Carica il file .env
load_dotenv()

URL_GATEWAY = os.getenv("URL_GATEWAY")