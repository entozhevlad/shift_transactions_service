from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.app.services.transaction_service import TransactionService, TransactionType

router = APIRouter()


class TransactionCreateRequest(BaseModel):
    """Создание транзакции."""

    amount: float
    type: str


class DateRangeRequest(BaseModel):
    """Диапазон дат."""

    start: datetime
    end: datetime


# Создаем экземпляр сервиса транзакций
transaction_service = TransactionService()


@router.post('/transactions/')
async def create_transaction(request: TransactionCreateRequest, token: str):
    """Создание транзакции."""
    if token is ...:
        token = Query(...)
    user = transaction_service.decode_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid or expired token')

    try:
        transaction_type = TransactionType(request.type)
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid transaction type')

    transaction_service.create_transaction(
        token,
        request.amount,
        transaction_type,
    )

    return {'detail': 'Transaction created'}


@router.post('/transactions/report/')
async def get_transactions_report(request: DateRangeRequest, token: str):
    """Отчет о транзакциях."""
    if token is ...:
        token = Query(...)
    user = transaction_service.decode_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid or expired token')

    transactions = transaction_service.get_user_transactions(
        token,
        request.start,
        request.end,
    )
    return {'transactions': [tx.__dict__ for tx in transactions]}


@router.get('/healthz/ready')
async def health_check():
    """Проверка состояния."""
    return {'status': 'healthy'}


@router.post('/token_data/')
async def verify_by_token(token: str):
    """Проверка токена."""
    if token is ...:
        token = Query(...)
    user = transaction_service.decode_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid or expired token')
    return user
