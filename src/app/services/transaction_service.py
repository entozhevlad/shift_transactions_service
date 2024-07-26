import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List

logging.basicConfig(level=logging.DEBUG)

@dataclass
class User:
    """Класс, представляющий пользователя."""
    user_id: uuid.UUID
    first_name: str
    last_name: str

class TransactionType(Enum):
    """Перечисление типов транзакций."""
    debit = 'debit'
    credit = 'credit'

@dataclass
class Transaction:
    """Класс, представляющий транзакцию."""
    user_id: uuid.UUID
    amount: int
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
        self.users: Dict[uuid.UUID, User] = {}
        self.transactions: List[Transaction] = []
        self.reports: List[Report] = []

    def add_user(self, first_name: str, last_name: str) -> uuid.UUID:
        """Добавляет нового пользователя."""
        user_id = uuid.uuid4()
        user = User(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
        )
        self.users[user_id] = user
        logging.info(
            'Добавлен пользователь: {0}, {1} {2}'.format(
                user_id, first_name, last_name,
            ),
        )
        return user.user_id

    def create_transaction(
        self, user_id: uuid.UUID, amount: float, trans_type: TransactionType,
    ) -> str:
        """Создает новую транзакцию."""
        if user_id not in self.users:
            logging.error(f'User ID not found: {user_id}')
            raise ValueError('User ID does not exist')
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type=trans_type,
        )
        self.transactions.append(transaction)
        return 'Транзакция создана: {0}\n'.format(transaction)

    def get_user_transactions(
        self, user_id: uuid.UUID, start: datetime, end: datetime,
    ) -> List[Transaction]:
        """Получает список транзакций пользователя за указанный период."""
        if user_id not in self.users:
            raise ValueError('User ID does not exist')
        return [
            transact
            for transact in self.transactions
            if transact.user_id == user_id and start <= transact.time <= end
        ]

    def save_report(
        self, user_id: uuid.UUID, transactions: List[Transaction],
    ) -> None:
        """Создает и сохраняет отчет по транзакциям пользователя."""
        report = Report(
            user_id=user_id,
            transactions=transactions,
        )
        self.reports.append(report)
        logging.info(
            'Отчёт для пользователя {user_id} {generated_at}'.format(
                user_id=user_id, generated_at=report.generated_at,
            ),
        )
        for transaction in report.transactions:
            logging.info(transaction)
        logging.info('')
