from flask import Flask
from authlib.integrations.flask_client import OAuth
import logging

# Inizializza l'app Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Chiave segreta per la sessione Flask

# Inizializza OAuth
oauth = OAuth(app)

# Configura il client_secret per Keycloak
#client_secret_value = "GBIYfiboZLalSc6Lax5P9rjZWUV1TiMm" #Peppe con OTP
client_secret_value = "cjiZXr4kq9F9c9Wv1zCbngSLkdUuNuPY" #Angelo senza OTP

# Configura Keycloak per l'autenticazione
keycloak = oauth.register(
    'keycloak',
    client_id='Client1',  # ID del client registrato in Keycloak
    client_secret=client_secret_value,  # Secret del client
    authorization_endpoint='http://localhost:8080/realms/Realm1/protocol/openid-connect/auth',  # Endpoint per l'autorizzazione
    token_endpoint='http://localhost:8080/realms/Realm1/protocol/openid-connect/token',  # Endpoint per il token
    jwks_uri='http://localhost:8080/realms/Realm1/protocol/openid-connect/certs',  # Certificati pubblici per la verifica JWT
    client_kwargs={'scope': 'openid profile email'},  # Scope richiesti
    metadata={'issuer': 'http://localhost:8080/realms/Realm1'}  # Informazioni sul provider OIDC
)

# Configura il logging per errori
logging.basicConfig(filename='logs\exercise_errors.log', level=logging.ERROR)  # Logga gli errori su file