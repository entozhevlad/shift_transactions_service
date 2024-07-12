import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict
from enum import Enum

logging.basicConfig(level=logging.DEBUG)


@dataclass
class User:
    """
    Класс, представляющий пользователя.
    """
    user_id: uuid.UUID
    first_name: str
    last_name: str


class TransactionType(Enum):
    """
    Перечисление типов транзакций.
    """
    DEBIT = "списать"
    CREDIT = "пополнить"


@dataclass
class Transaction:
    """
    Класс, представляющий транзакцию.
    """
    user_id: uuid.UUID
    amount: int
    type: TransactionType
    time: datetime = field(default_factory=datetime.now)


@dataclass
class Report:
    """
    Класс, представляющий отчет по транзакциям.
    """
    user_id: uuid.UUID
    transactions: List[Transaction]
    generated_at: datetime = field(default_factory=datetime.now)


class TransactionService:
    def __init__(self):
        """
        Инициализирует сервис транзакций.
        """

        self.users: Dict[uuid.UUID, User] = {}
        self.transactions: List[Transaction] = []
        self.reports: List[Report] = []

    def add_user(self, first_name: str, last_name: str) -> uuid.UUID:
        """
        Добавляет нового пользователя.

        """
        user_id = uuid.uuid4()
        user = User(user_id, first_name, last_name)
        self.users[user_id] = user
        logging.info(f"User added: {user_id}, {first_name} {last_name}")
        return user.user_id

    def create_transaction(self, user_id: uuid.UUID, amount: float, type: TransactionType) -> str:
        """
        Создает новую транзакцию.

        """
        if user_id not in self.users:
            logging.error(f"User ID not found: {user_id}")
            raise ValueError('Пользователь с таким ID не существует')
        transaction = Transaction(user_id, amount, type)
        self.transactions.append(transaction)
        return f"Транзакция создана: {transaction}\n"

    def get_transactions(self, user_id: uuid.UUID, start: datetime, end: datetime) -> List[Transaction]:
        """
        Получает список транзакций пользователя за указанный период.

        """
        if user_id not in self.users:
            raise ValueError('Пользователь с таким ID не существует')
        transactions = [
            transaction for transaction in self.transactions
            if transaction.user_id == user_id and start <= transaction.time <= end
        ]
        return transactions

    def save_report(self, user_id: uuid.UUID, transactions: List[Transaction]) -> None:
        """
        Создает и сохраняет отчет по транзакциям пользователя.
        """
        report = Report(user_id, transactions)
        self.reports.append(report)
        logging.info(f"Report for user {user_id} generated at {
                     report.generated_at}")
        for transaction in report.transactions:
            logging.info(transaction)
        logging.info("")
