from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel
from datetime import datetime
from src.app.services.transaction_service import TransactionService, TransactionType
import uuid
from dataclasses import dataclass
from typing import Optional


SECRET_KEY='eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTcyMDA4MTcxNywiaWF0IjoxNzIwMDgxNzE3fQ.pVVn3P7Fzl62b6O-Qge0TpUiA75zu1rNGXpzwykkRHc'
ALGORITHM = "HS256"

router = APIRouter()

@dataclass
class User:
    """Класс, представляющий пользователя."""
    username: str
    password: str
    user_id: uuid.UUID
    first_name: str
    last_name: str
    token: Optional[str] = None

class TransactionCreateRequest(BaseModel):
    amount: float
    type: str

class DateRangeRequest(BaseModel):
    start: datetime
    end: datetime

# Создаем экземпляр сервиса транзакций
transaction_service = TransactionService()

async def get_current_user_id(authorization: str = Header(...)) -> uuid.UUID:
    token = authorization.split(" ")[1]
    try:
        # Декодируем токен для получения user_id
        user_id = transaction_service._decode_token(token)
        return user_id
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/transactions/")
async def create_transaction(request: TransactionCreateRequest, authorization: str = Header(...)):
    user_id = await get_current_user_id(authorization)
    try:
        transaction_type = TransactionType(request.type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    transaction_service.create_transaction(
        authorization, request.amount, transaction_type
    )

    return {"detail": "Transaction created"}

@router.post("/transactions/report/")
async def get_transactions_report(request: DateRangeRequest, authorization: str = Header(...)):
    user_id = await get_current_user_id(authorization)
    transactions = transaction_service.get_user_transactions(
        authorization, request.start, request.end
    )
    return {"transactions": [t.__dict__ for t in transactions]}

@router.get("/healthz/ready")
async def health_check():
    """Проверка состояния сервиса."""
    return {"status": "healthy"}

@router.post("/token_data/")
async def verify_by_token(token: str = Query(...)):
    """Проверяет валидность токена и возвращает информацию о пользователе."""
    user = transaction_service.decode_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {
        "username": user,
    }