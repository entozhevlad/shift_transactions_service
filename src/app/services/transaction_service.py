import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import jwt
from decouple import config

logging.basicConfig(level=logging.DEBUG)

# Constants for repeated string literals
ALGORITHM = 'HS256'
SECRET_KEY = config('SECRET_KEY')
USERNAME_FIELD = 'username'
USER_ID_FIELD = 'user_id'


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

    def __init__(self):
        """Инициализирует сервис транзакций."""
        self.transactions: List[Transaction] = []
        self.reports: List[Report] = []

    def decode_token(self, token: str) -> Optional[Dict[str, str]]:
        """Проверяет JWT-токен и извлекает полную информацию о пользователе."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.PyJWTError:
            return None

        username: Optional[str] = payload.get(USERNAME_FIELD)
        user_id: Optional[str] = payload.get(USER_ID_FIELD)
        if username is None or user_id is None:
            return None
        return {USERNAME_FIELD: username, USER_ID_FIELD: user_id}

    def create_transaction(
        self, token: str, amount: float, trans_type: TransactionType,
    ) -> str:
        """Создает новую транзакцию."""
        user_info = self.decode_token(token)
        if user_info is None:
            return 'Invalid token'

        transaction = Transaction(
            user_id=user_info.get(USER_ID_FIELD),
            amount=amount,
            type=trans_type,
        )
        self.transactions.append(transaction)
        return 'Transaction created for user {user_id}: {transaction}'.format(
            user_id=user_info.get(USER_ID_FIELD), transaction=transaction,
        )

    def get_user_transactions(
        self, token: str, start: datetime, end: datetime,
    ) -> List[Transaction]:
        """Получает список транзакций пользователя за указанный период."""
        user_info = self.decode_token(token)
        if user_info is None:
            return []

        return [
            transact
            for transact in self.transactions
            if (
                transact.user_id == user_info.get(USER_ID_FIELD)
                and start <= transact.time <= end
            )
        ]

    def save_report(
        self, token: str, transactions: List[Transaction],
    ) -> None:
        """Создает и сохраняет отчет по транзакциям пользователя."""
        user_info = self.decode_token(token)
        if user_info is None:
            logging.error('Invalid token provided for report generation.')
            return

        report = Report(
            user_id=user_info.get(USER_ID_FIELD),
            transactions=transactions,
        )
        self.reports.append(report)
        logging.info(
            'Отчёт для пользователя {user_id} {generated_at}'.format(
                user_id=report.user_id,
                generated_at=report.generated_at,
            ),
        )
        for transaction in report.transactions:
            logging.info(transaction)
        logging.info('')
