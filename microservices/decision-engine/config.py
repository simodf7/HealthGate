from dotenv import load_dotenv
import os

# Carica il file .env
load_dotenv()

# Recupera le variabili
API_KEY = os.getenv("API_KEY")
AGGREGATOR_SERVICE = os.getenv("AGGREGATOR_SERVICE")
AGGREGATOR_ROUTE = os.getenv("AGGREGATOR_ROUTE")