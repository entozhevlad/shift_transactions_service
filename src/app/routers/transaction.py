from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from src.app.services.transaction_service import TransactionService, TransactionType
from uuid import UUID
from datetime import datetime

router = APIRouter()

class UserCreateRequest(BaseModel):
    first_name: str
    last_name: str

class TransactionCreateRequest(BaseModel):
    user_id: UUID
    amount: float
    type: str  # Используем строку

class DateRangeRequest(BaseModel):
    start: datetime
    end: datetime
    user_id: UUID

transaction_service = TransactionService()

@router.post("/users/", response_model=UUID)
async def create_user(request: UserCreateRequest):
    user_id = transaction_service.add_user(request.first_name, request.last_name)
    return user_id

@router.post("/transactions/")
async def create_transaction(request: TransactionCreateRequest):
    try:
        transaction_type = TransactionType(request.type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    try:
        transaction_service.create_transaction(
            request.user_id, request.amount, transaction_type
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="User ID does not exist")

    return {"detail": "Transaction created"}

@router.post("/transactions/report/")
async def get_transactions_report(request: DateRangeRequest):
    transactions = transaction_service.get_user_transactions(
        request.user_id, request.start, request.end
    )
    return {"transactions": [t.__dict__ for t in transactions]}
