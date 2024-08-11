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

    def get_user_transactions(
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

    def save_report(
        self, username: str, transactions: List[Transaction],
    ) -> None:
        """Создает и сохраняет отчет по транзакциям пользователя."""
        user = await self._get_user_from_auth_service(username)
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
