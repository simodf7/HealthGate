# 1. Immagine base con Python 3.13
FROM python:3.13-slim

# 2. Imposta la cartella di lavoro
WORKDIR /app

# 3. Copia i file delle dipendenze
COPY requirements.txt .

# 4. Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia tutto il codice
COPY . .

# 6. Espone la porta su cui gira FastAPI
EXPOSE 8002

# 7. Comando per avviare l'app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

