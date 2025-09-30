from dotenv import load_dotenv
import os

# Carica il file .env
load_dotenv()

# Recupera le variabili
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))
DATABASE_URL = os.getenv("DATABASE_URL")