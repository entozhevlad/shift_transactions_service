import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
import jwt
from decouple import config
from typing import Optional


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

ALGORITHM = "HS256"
SECRET_KEY = config('SECRET_KEY')


class TransactionService:
    """Сервис для управления транзакциями."""
    def __init__(self):
        """Инициализирует сервис транзакций."""
        self.transactions: List[Transaction] = []
        self.reports: List[Report] = []

    def decode_token(self, token: str):
        """Проверяет JWT-токен и извлекает полную информацию о пользователе."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("username")
            user_id: str = payload.get("user_id")
            if username is None or user_id is None:
                return None
            return {'username': username, 'user_id': user_id}
        except jwt.PyJWTError:
            return None

    def create_transaction(
        self, token: str, amount: float, trans_type: TransactionType
    ) -> str:
        """Создает новую транзакцию."""
        user_id = self.decode_token(token)
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type=trans_type,
        )
        self.transactions.append(transaction)
        return f'Transaction created for user {user_id}: {transaction}'

    def get_user_transactions(
        self, token: str, start: datetime, end: datetime
    ) -> List[Transaction]:
        """Получает список транзакций пользователя за указанный период."""
        user_id = self.decode_token(token)
        return [
            transact
            for transact in self.transactions
            if transact.user_id == user_id and start <= transact.time <= end
        ]

    def save_report(
        self, token: str, transactions: List[Transaction],
    ) -> None:
        """Создает и сохраняет отчет по транзакциям пользователя."""
        user_id = self._decode_token(token)
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
