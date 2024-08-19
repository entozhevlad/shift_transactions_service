from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.db.db import get_db
from src.app.services.transaction_service import TransactionService, TransactionType
from datetime import datetime

class DateRangeRequest(BaseModel):
    """Модель для диапазона дат."""
    start: datetime
    end: datetime

class TransactionCreateRequest(BaseModel):
    """Модель для создания транзакции."""
    amount: float
    type: str

router = APIRouter()

AUTH_SERVICE_URL = 'http://auth_service:82'

@router.post('/transactions/')
async def create_transaction(
    request: TransactionCreateRequest,
    token: str = Header(...),  # JWT токен передается через заголовок
    db_session: AsyncSession = Depends(get_db)
):
    """Создание транзакции."""
    transaction_service = TransactionService(db_session=db_session, auth_service_url=AUTH_SERVICE_URL)

    result = await transaction_service.update_user_balance(
        token=token,
        amount=request.amount,  # Используйте только amount из запроса
        transaction_type=TransactionType(request.type),  # Тип транзакции
    )

    if "Transaction created" not in result:
        raise HTTPException(status_code=400, detail=result)

    return {'detail': 'Transaction created'}


@router.post('/transactions/report/')
async def get_transactions_report(
    request: DateRangeRequest,
    token: str = Header(...),  # JWT токен передается через заголовок
    db_session: AsyncSession = Depends(get_db)
):
    """Отчет о транзакциях."""
    transaction_service = TransactionService(db_session=db_session, auth_service_url=AUTH_SERVICE_URL)

    transactions = await transaction_service.get_user_transactions(
        token,
        request.start,
        request.end,
    )

    return {'transactions': [tx.__dict__ for tx in transactions]}
