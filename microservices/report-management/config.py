from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "healthgate_db")

SERVICE_URL = os.getenv("SERVICE_URL") 
ROUTE = os.getenv("ROUTE") 