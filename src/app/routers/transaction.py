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

transaction_service = TransactionService()

async def get_current_user(authorization: str = Header(...)) -> str:
    token = authorization.split(" ")[1]
    async with httpx.AsyncClient() as client:
        response = await client.get("http://auth-service/validate_token", headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_info = response.json()
        return user_info["username"]

@router.post("/transactions/")
async def create_transaction(request: TransactionCreateRequest, username: str = Depends(get_current_user)):
    try:
        transaction_type = TransactionType(request.type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    try:
        transaction_service.create_transaction(
            username, request.amount, transaction_type
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="User does not exist")

    return {"detail": "Transaction created"}

@router.post("/transactions/report/")
async def get_transactions_report(request: DateRangeRequest, username: str = Depends(get_current_user)):
    transactions = transaction_service.get_user_transactions(
        username, request.start, request.end
    )
    return {"transactions": [t.__dict__ for t in transactions]}

@router.get("/healthz/ready")
async def health_check():
    return {"status": "healthy"}