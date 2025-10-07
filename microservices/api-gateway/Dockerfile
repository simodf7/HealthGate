# Usa un'immagine base
FROM python:3.12-slim

# Imposta la cartella di lavoro
WORKDIR /app

# Copia i file del progetto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Espone la porta su cui gira il servizio
EXPOSE 5000

# Comando per avviare il servizio
CMD ["python", "app.py"]
