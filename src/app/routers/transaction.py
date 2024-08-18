from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.transaction_service import TransactionService, TransactionType
from src.app.db.db import get_db

router = APIRouter()

# Указываем URL сервиса аутентификации
AUTH_SERVICE_URL = 'http://auth_service:82'

# Инициализация сервиса транзакций один раз
transaction_service = TransactionService(auth_service_url=AUTH_SERVICE_URL, db_session=None)

class TransactionCreateRequest(BaseModel):
    """Создание транзакции."""
    amount: float
    type: str

class DateRangeRequest(BaseModel):
    """Диапазон дат."""
    start: datetime
    end: datetime

@router.post('/transactions/')
async def create_transaction(
    request: TransactionCreateRequest,
    token: str,
    db_session: AsyncSession = Depends(get_db)
):
    """Создание транзакции."""
    # Передаем текущую сессию в сервис
    transaction_service.db_session = db_session

    result = await transaction_service.update_user_balance(
        token,
        request.amount,
        TransactionType(request.type),
    )

    if "Transaction created" not in result:
        raise HTTPException(status_code=400, detail=result)

    return {'detail': 'Transaction created'}

@router.post('/transactions/report/')
async def get_transactions_report(
    request: DateRangeRequest,
    token: str,
    db_session: AsyncSession = Depends(get_db)
):
    """Отчет о транзакциях."""
    # Передаем текущую сессию в сервис
    transaction_service.db_session = db_session

    transactions = await transaction_service.get_user_transactions(
        token,
        request.start,
        request.end,
    )

    return {'transactions': [tx.__dict__ for tx in transactions]}
