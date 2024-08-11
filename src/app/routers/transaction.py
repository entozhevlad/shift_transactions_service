from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from datetime import datetime
from typing import List
import httpx
from src.app.services.transaction_service import TransactionService, TransactionType

router = APIRouter()

class TransactionCreateRequest(BaseModel):
    amount: float
    type: str

class DateRangeRequest(BaseModel):
    start: datetime
    end: datetime

# URL микросервиса авторизации
AUTH_SERVICE_URL = "http://auth_service:82"

# Создаем экземпляр сервиса транзакций
transaction_service = TransactionService(auth_service_url=AUTH_SERVICE_URL)

async def get_current_user(authorization: str = Header(...)) -> str:
    token = authorization.split(" ")[1]
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AUTH_SERVICE_URL}/verify", headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_info = response.json()
        return user_info["username"]

@router.post("/transactions/")
async def create_transaction(request: TransactionCreateRequest, authorization: str = Header(...)):
    username = await get_current_user(authorization)
    try:
        transaction_type = TransactionType(request.type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    try:
        await transaction_service.create_transaction(
            username, request.amount, transaction_type, token=authorization
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="User does not exist")

    return {"detail": "Transaction created"}

@router.post("/transactions/report/")
async def get_transactions_report(request: DateRangeRequest, authorization: str = Header(...)):
    username = await get_current_user(authorization)
    transactions = await transaction_service.get_user_transactions(
        username, request.start, request.end, token=authorization
    )
    return {"transactions": [t.__dict__ for t in transactions]}

@router.get("/healthz/ready")
async def health_check():
    """Проверка состояния сервиса."""
    return {"status": "healthy"}
