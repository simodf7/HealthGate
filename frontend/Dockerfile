# frontend/Dockerfile

FROM python:3.11-slim

# 2. Imposta la cartella di lavoro
WORKDIR /app

# 3. Copia i file delle dipendenze
COPY requirements.txt .

# 4. Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia tutto il codice
COPY . .

# 6. Espone la porta su cui gira FastAPI
EXPOSE 8501

# 7. Comando per avviare l'app
CMD ["streamlit", "run", "HealthGate.py", "--server.port=8501", "--server.address=0.0.0.0"]
