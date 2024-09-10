from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
import json

from src.app.db.db import get_db
from src.app.services.transaction_service import TransactionService, TransactionType


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


def get_redis() -> Redis:
    return Redis(host='redis', port=6379, db=0, decode_responses=True)

@router.post('/transactions/')
async def create_transaction(
    request: TransactionCreateRequest,
    token: str = Header(...),  # JWT токен передается через заголовок
    db_session: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(get_redis),  # Добавляем Redis в зависимости
):
    """Создание транзакции."""
    transaction_service = TransactionService(
        db_session=db_session,
        auth_service_url=AUTH_SERVICE_URL,
    )

    # Очистка кэша транзакций для этого пользователя при создании новой транзакции
    redis_client.delete(f"transactions:{token}")

    responce_result = await transaction_service.update_user_balance(
        token=token,
        amount=request.amount,  # Используйте только amount из запроса
        transaction_type=TransactionType(request.type),  # Тип транзакции
    )

    if 'Transaction created' not in responce_result:
        raise HTTPException(status_code=400, detail=responce_result)

    return {'detail': 'Transaction created'}


@router.post('/transactions/report/')
async def get_transactions_report(
    request: DateRangeRequest,
    token: str = Header(...),
    db_session: AsyncSession = Depends(get_db),
     redis_client: Redis = Depends(get_redis),  # Добавляем Redis в зависимости
):
    """Отчет о транзакциях."""
    cache_key = f"transactions:{token}:{request.start}:{request.end}"
    cached_transactions = redis_client.get(cache_key)

    if cached_transactions:
        # Если данные есть в кэше, возвращаем их
        transactions = json.loads(cached_transactions)
        return {'transactions': transactions}

    transaction_service = TransactionService(
        db_session=db_session,
        auth_service_url=AUTH_SERVICE_URL,
    )

    transactions = await transaction_service.get_user_transactions(
        token,
        request.start,
        request.end,
    )

    # Кэшируем результат на 60 секунд
    redis_client.setex(cache_key, 60, json.dumps([tx.__dict__ for tx in transactions]))

    return {'transactions': [tx.__dict__ for tx in transactions]}


@router.get('/healthz/ready')
async def health_check():
    """Проверка доступности сервиса."""
