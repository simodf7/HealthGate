from dotenv import load_dotenv
import os

# Carica il file .env
load_dotenv()


AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
ROUTE_AUTH_SERVICE = os.getenv("ROUTE_AUTH_SERVICE")
REPORT_SERVICE_URL = os.getenv("REPORT_SERVICE_URL")
ROUTE_REPORT_SERVICE= os.getenv("ROUTE_REPORT_SERVICE")