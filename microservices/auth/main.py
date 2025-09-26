from fastapi import FastAPI

app = FastAPI(title="Authentication Service")

@app.post("/signup", response_model=dict)
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    user = await create_user(db, data.username, data.password)
    return {"id": user.id, "username": user.username}

@app.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    token = await authenticate_user(db, data.username, data.password)
    return {"access_token": token, "token_type": "bearer"}