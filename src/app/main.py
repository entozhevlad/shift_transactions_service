from fastapi import FastAPI
from src.app.routers import transaction_router

app = FastAPI()

@app.get("/")
def read_main():
    return {"message": "Welcome to the Transaction Service API"}

app.include_router(transaction_router.router, prefix="/transaction", tags=["transaction"])
