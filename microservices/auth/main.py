from fastapi import FastAPI
import database as db

app = FastAPI(title="Authentication Service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db() # All'avvio inizializzo il database
    yield  # to be executed at shutdown

@app.post("/signup", response_model=dict)
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    user = await create_user(db, data.username, data.password)
    return {"id": user.id, "username": user.username}

@app.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    token = await authenticate_user(db, data.username, data.password)
    return {"access_token": token, "token_type": "bearer"}

'''
@app.post("/login")
def login(username: str, password: str):
    # validazione utente (qui finto)
    user_id = "user-123"
    access_token = create_access_token(user_id, scopes=["read:items"])
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected")
def protected_route(token: str):
    payload = verify_token(token)
    return {"msg": f"Benvenuto utente {payload['sub']}"}

# --- route ---
@app.get("/profilo")
def get_profilo(token_payload = Depends(require_paziente)):
    return {"msg": f"Accesso consentito a {token_payload['sub']} come paziente"}

@app.get("/cartella_clinica")
def get_cartella(token_payload = Depends(require_operatore)):
    return {"msg": f"Accesso consentito a {token_payload['sub']} come operatore sanitario"}
'''