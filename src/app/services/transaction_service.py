import httpx
import uuid
from datetime import datetime
from typing import List, Optional
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from src.app.db.models import TransactionModel

class TransactionType(Enum):
    """Перечисление типов транзакций."""
    debit = 'debit'
    credit = 'credit'

class TransactionService:
    """Сервис для управления транзакциями."""

    def __init__(self, auth_service_url: str, db_session: AsyncSession):
        self.auth_service_url = auth_service_url
        self.db_session = db_session

    async def decode_token(self, token: str) -> Optional[dict]:
        """Декодирование токена для получения информации о пользователе."""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.auth_service_url}/token_data/", json={"token": token})
            if response.status_code == 200:
                return response.json()
            return None

    async def update_user_balance(self, token: str, amount: float, transaction_type: TransactionType) -> Optional[str]:
        """Обновление баланса пользователя и создание транзакции."""
        user_info = await self.decode_token(token)
        if user_info is None:
            return "Invalid token."

        user_id = user_info.get('user_id')

        async with httpx.AsyncClient() as client:
            # Получаем текущий баланс пользователя
            balance_response = await client.get(f"{self.auth_service_url}/users/{user_id}/get_balance")
            if balance_response.status_code != 200:
                return "User not found."

            current_balance = balance_response.json().get("balance")

            if transaction_type == TransactionType.debit and current_balance < amount:
                return f"Insufficient funds. Current balance: {current_balance}."

            new_balance = current_balance - amount if transaction_type == TransactionType.debit else current_balance + amount

            update_response = await client.patch(
                f"{self.auth_service_url}/users/{user_id}/update_balance",
                json={"new_balance": new_balance}
            )
            if update_response.status_code != 200:
                return "Failed to update balance."

            try:
                await self.create_transaction(user_id, amount, transaction_type)
            except Exception as e:
                return f"Failed to create transaction: {str(e)}"

            return f"Transaction created for user {user_id}."

    async def create_transaction(self, user_id: uuid.UUID, amount: float, transaction_type: TransactionType) -> None:
        """Создание записи транзакции в базе данных."""
        transaction = TransactionModel(
            id=uuid.uuid4(),
            user_id=user_id,
            amount=amount,
            type=transaction_type.value,
            created_at=datetime.utcnow()
        )

        async with self.db_session as session:
            async with session.begin():
                session.add(transaction)

    async def get_user_transactions(self, token: str, start: datetime, end: datetime) -> List[TransactionModel]:
        """Получение транзакций пользователя из базы данных по user_id."""
        user_info = await self.decode_token(token)
        if user_info is None:
            return []

        user_id = user_info.get('user_id')

        async with self.db_session as session:
            query = select(TransactionModel).where(
                TransactionModel.user_id == user_id,
                TransactionModel.created_at.between(start, end)
            )
            result = await session.execute(query)
            transactions = result.scalars().all()

        return transactions
