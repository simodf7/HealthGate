from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import httpx  
import jwt 
from config import SECRET_KEY, JWT_ALGORITHM, MICROSERVICES

"""
httpx è una libreria Python che ti permette di fare richieste 
HTTP (GET, POST, PUT, DELETE, ecc.) 
in modo semplice, un po' come requests, ma con alcune differenze:
•	supporta sia codice sincrono che asincrono (AsyncClient),
•	gestisce connessioni persistenti (connection pooling),

"""

# creiamo un client httpx.AsyncClient allo startup 
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient()
    yield  # to be executed at shutdown
    await app.state.client.aclose()
 
app = FastAPI(title="API Gateway", lifespan=lifespan)





"""
# autenticazione jwt
async def verify_jwt(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token mancante")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        request.state.user = payload  # salviamo l’utente per usi successivi
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token scaduto")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")
"""

# --- verifica token e controllo ruolo generico ---
async def verify_jwt_with_role(request: Request, required_role: str):
    """
    Verifica firma e scadenza del token e controlla che l'utente
    abbia il ruolo richiesto.
    """
    print(request.headers)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token mancante")

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token scaduto")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token non valido")

    # Controllo ruolo
    role = payload.get("scope")

    if role != required_role:
        raise HTTPException(status_code=403, detail="Permesso negato")    

    request.state.user = {"user_id": payload.get("sub"), "role": role, "expiry": payload.get("exp")}
    return 


# Funzione di proxy verso i microservizi
async def proxy_request(request: Request, method: str, service_url: str, role: str = None):
    
    path = request.url.path
    
    if not path.startswith(("/login","/signup")):
        # await verify_jwt(request)
        await verify_jwt_with_role(request, role)

    url = f"{service_url}{request.url.path}"  # concateniamo con l'url del microservizio es. /localhost:8001


    """
    Esempio: 
    # Richiesta originale al gateway:
    GET http://localhost:8000/users/42/profile

    # service_url (microservizio utenti):
    service_url = "http://localhost:8001"

    # Risultato finale:
    url = "http://localhost:8001/users/42/profile"

    """

    # è inutile ricavare il body se ho una get o head
    if method in ["post", "put", "patch", "delete"]:
        body = await request.body()
    else: 
        body = None

    headers = dict(request.headers)

    # Se l’utente è autenticato, aggiungo info interne - Strategia microservizi si fidano del controllo gateway sul token 
    if hasattr(request.state, "user"):
        headers["X-User-Id"] = str(request.state.user["user_id"])
        headers["X-User-Role"] = str(request.state.user.get("role", "user"))
        headers["X-User-Expiry"] = str(request.state.user.get("expiry", ""))
        headers.pop("Authorization", None)  # il microservizio non ha bisogno del token

    # Richiesta al microservizio
    response = await app.state.client.request(method, url, content=body, headers=headers)
 
    return Response(content=response.content, status_code=response.status_code, headers=response.headers)
 

# Health check endpoint to verify if gateway is properly running
@app.get("/")
def health_check():
    return{"status": "API Gateway running"}


### Auth service routes 

# Registrazione
@app.post("/signup/operator") 
async def signup_proxy(request: Request):
    return await proxy_request(request, "post", MICROSERVICES["auth"])

# Registrazione
@app.post("/signup/patient") 
async def signup_proxy(request: Request):
    return await proxy_request(request, "post", MICROSERVICES["auth"])

# Login 
@app.post("/login/patient")
async def signup_proxy(request: Request):
    return await proxy_request(request, "post", MICROSERVICES["auth"])


# Login 
@app.post("/login/operator")
async def signup_proxy(request: Request):
    return await proxy_request(request, "post", MICROSERVICES["auth"])




## Ingestion service route
@app.post("/ingestion")
async def ingestion_proxy(request: Request):
    # Richiede ruolo operator (es. medico che invia audio)
    return await proxy_request(request, "post", MICROSERVICES["ingest"], "patient")


## Decision engine service route
@app.get("/llm")
async def signup_proxy(request: Request):
    return await proxy_request(request, "get", MICROSERVICES["decision"], "patient")

"""
# Routing dinamico
@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def users_proxy(path: str, request: Request, user=Depends(get_current_user)):
    return await proxy_request(request, MICROSERVICES["users"])
 
@app.api_route("/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def orders_proxy(path: str, request: Request, user=Depends(get_current_user)):
    return await proxy_request(request, MICROSERVICES["orders"])
"""