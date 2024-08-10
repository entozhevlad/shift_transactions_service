import logging
from datetime import datetime
from fastapi import FastAPI
from src.app.routers import transaction
from src.app.services.transaction_service import TransactionService, TransactionType

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

transactions = [50, 100, 200]
date = [(2023, 1, 1), (2024, 12, 31)]
st = datetime(*date[0])
end = datetime(*date[1])

app = FastAPI()

@app.get("/")
def read_main():
    return {"message": "Welcome to the Transaction Service API"}

app.include_router(transaction.router, prefix="/transaction", tags=["transaction"])
