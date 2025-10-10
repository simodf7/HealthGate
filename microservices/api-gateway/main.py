# python -m uvicorn main:app  --reload --host 0.0.0.0 --port 8000
# Invoke-RestMethod -Uri "http://localhost:8000/signup/patient" -Method POST -Headers @{ "Content-Type" = "application/json" } ` -Body '{"firstname":"Rita","lastname":"Castaldi","birth_date":"2001-08-09", "sex":"F","birth_place":"Napoli","password":"Password124"}'
# Invoke-RestMethod -Uri "http://localhost:8000/signup/patient" -Method POST -Headers @{ "Content-Type" = "application/json" } ` -Body '{"firstname":"Alessandro","lastname":"Campanella","birth_date":"2001-11-27", "sex":"M","birth_place":"Napoli","password":"Password124"}'
# Invoke-RestMethod -Uri "http://localhost:8000/signup/operator" -Method POST -Headers @{ "Content-Type" = "application/json" } -Body '{"med_register_code":"MED123456","firstname":"Giulia","lastname":"Rossi","email":"giulia.rossi@example.com","phone_number":"+393331112233","password":"SecurePass!2025"}'


from fastapi import FastAPI, Request, HTTPException, Response
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
    app.state.client = httpx.AsyncClient(timeout=20.0)
    yield  # to be executed at shutdown
    await app.state.client.aclose()
 
app = FastAPI(title="API Gateway", lifespan=lifespan)



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
    
    target_path = request.url.path
    
    if not target_path.startswith(("/login","/signup")):
        # await verify_jwt(request)
        await verify_jwt_with_role(request, role)

    if target_path.startswith("/diagnose"): # da vedere se ci piace
        target_path = "/ingestion"   # localhost:8000/diagnose ->> localhost:8002/ingestion

    # localhost:8000/ingestion ->>   localhost:8002/ingestion

    url = f"{service_url}{target_path}"  # concateniamo con l'url del microservizio es. /localhost:8001

    print(url)
  

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
    try:
        response = await app.state.client.request(method, url, content=body, headers=headers)
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="Timeout durante la comunicazione")

 
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


# Get User data

@app.get("/user/profile/{patient_id}")
async def user_proxy(request: Request):
    return await proxy_request(request, "post", MICROSERVICES['auth'])




"""  Uniti in un'unica rotta
## Ingestion service route
@app.post("/ingestion")
async def ingestion_proxy(request: Request):
    # Richiede ruolo operator (es. medico che invia audio)
    return await proxy_request(request, "post", MICROSERVICES["ingest"], "patient")


## Decision engine service route
@app.get("/llm")
async def signup_proxy(request: Request):
    return await proxy_request(request, "get", MICROSERVICES["decision"], "patient")

@app.post("/llm/diagnose")
async def signup_proxy(request: Request):
    return await proxy_request(request, "post", MICROSERVICES["decision"], "patient")

"""



@app.post("/diagnose")  # ingest richiamerà decision
async def diagnose_proxy(request: Request):
    return await proxy_request(request, "post", MICROSERVICES["ingest"], "patient")



## report 


## ROUTE PER RICAVARE I REPORT DI UN PAZIENTE

@app.get("/reports/id/{patient_id}")
async def find_reports_proxy(request: Request):
    return await proxy_request(request, "get", MICROSERVICES["report"], "patient")


@app.get("/reports/ssn/{social_sec_number}")
async def find_reports_proxy(request: Request):
    return await proxy_request(request, "get", MICROSERVICES["report"], "operator")


## ROUTE PER AGGIORNARE UN SINGOLO REPORT
@app.put("/report/{report_id}")
async def update_report_proxy(request: Request):
    return await proxy_request(request, "put", MICROSERVICES["report"], "operator")

    
## ROUTE PER GENERARE UN PDF 
@app.get("/report/pdf/{report_id}")
async def pdf_report_proxy(request: Request):
    return await proxy_request(request, "get", MICROSERVICES['report'])


