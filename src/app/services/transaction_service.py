import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
import httpx  # Для выполнения HTTP-запросов

logging.basicConfig(level=logging.DEBUG)

class TransactionType(Enum):
    """Перечисление типов транзакций."""
    debit = 'debit'
    credit = 'credit'

@dataclass
class Transaction:
    """Класс, представляющий транзакцию."""
    user_id: uuid.UUID
    amount: float
    type: TransactionType
    time: datetime = field(default_factory=datetime.now)

@dataclass
class Report:
    """Класс, представляющий отчет по транзакциям."""
    user_id: uuid.UUID
    transactions: List[Transaction]
    generated_at: datetime = field(default_factory=datetime.now)

class TransactionService:
    """Сервис для управления транзакциями."""
    def __init__(self, auth_service_url: str):
        """Инициализирует сервис транзакций."""
        self.transactions: List[Transaction] = []
        self.reports: List[Report] = []
        self.auth_service_url = auth_service_url

    async def _get_user_from_auth_service(self, username: str, token: str):
        """Получает пользователя из микросервиса авторизации."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.auth_service_url}/verify", headers={"Authorization": f"Bearer {token}"})
            if response.status_code == 200:
                return response.json()["user"]
            else:
                raise ValueError("User does not exist in the auth service")

    async def create_transaction(
        self, username: str, amount: float, trans_type: TransactionType, token: str
    ) -> str:
        """Создает новую транзакцию."""
        user = await self._get_user_from_auth_service(username, token)
        user_id = uuid.UUID(user["user_id"])
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type=trans_type,
        )
        self.transactions.append(transaction)
        return f'Transaction created for user {username}: {transaction}'

    async def get_user_transactions(
        self, username: str, start: datetime, end: datetime, token: str
    ) -> List[Transaction]:
        """Получает список транзакций пользователя за указанный период."""
        user = await self._get_user_from_auth_service(username, token)
        user_id = uuid.UUID(user["user_id"])
        return [
            transact
            for transact in self.transactions
            if transact.user_id == user_id and start <= transact.time <= end
        ]

    async def save_report(
        self, username: str, transactions: List[Transaction], token: str
    ) -> None:
        """Создает и сохраняет отчет по транзакциям пользователя."""
        user = await self._get_user_from_auth_service(username, token)
        user_id = uuid.UUID(user["user_id"])
        report = Report(
            user_id=user_id,
            transactions=transactions,
        )
        self.reports.append(report)
        logging.info(
            'Отчёт для пользователя {user_id} {generated_at}'.format(
                user_id=report.user_id, generated_at=report.generated_at,
            ),
        )
        for transaction in report.transactions:
            logging.info(transaction)
        logging.info('')


# transaction.py
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
