from fastapi import FastAPI
from app.auth.routes import router as auth_router

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

app.include_router(auth_router, prefix="/auth", tags=["Auth"])