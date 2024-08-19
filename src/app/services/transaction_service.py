import httpx
import jwt
import uuid
from datetime import datetime
from typing import List, Optional
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.app.db.models import TransactionModel
from decouple import config

# Конфигурация для декодирования JWT
SECRET_KEY = config('SECRET_KEY')
ALGORITHM = 'HS256'

class TransactionType(Enum):
    """Перечисление типов транзакций."""
    debit = 'debit'   # Уменьшение баланса
    credit = 'credit' # Увеличение баланса

class TransactionService:
    """Сервис для управления транзакциями."""

    def __init__(self, db_session: AsyncSession, auth_service_url: str):
        self.db_session = db_session
        self.auth_service_url = auth_service_url

    def decode_token(self, token: str) -> Optional[dict]:
        """Декодирование токена для получения информации о пользователе."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    async def get_user_balance(self, token: str) -> Optional[float]:
        """Получение баланса пользователя через API микросервиса авторизации."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.auth_service_url}/users/balance",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                balance_info = response.json()
                return balance_info.get("balance")
            return None


    async def update_user_balance(self, token: str, amount: float, transaction_type: TransactionType) -> str:
        """Обновление баланса пользователя и создание транзакции."""
        # Предполагаем, что new_balance вычисляется где-то в методе или не требуется
        params = {
            "amount": amount,  # Передаем только amount
            "Authorization": token
        }

        async with httpx.AsyncClient() as client:
            update_response = await client.patch(
                f"{self.auth_service_url}/users/update_balance",
                params=params,  # Передаем параметры через URL
                headers={"accept": "application/json"}
            )

            if update_response.status_code == 422:
                return "Invalid parameters provided. Check the data being sent."

            if update_response.status_code != 200:
                return "Failed to update balance."

            # Создаем транзакцию в случае успешного обновления баланса
            try:
                await self.create_transaction(token, amount, transaction_type)
            except Exception as e:
                return f"Failed to create transaction: {str(e)}"

            return "Transaction created."


    async def create_transaction(self, token: str, amount: float, transaction_type: TransactionType) -> None:
        """Создание записи транзакции в базе данных."""
        user_info = self.decode_token(token)
        if not user_info:
            raise ValueError("Invalid token.")

        user_id = uuid.UUID(user_info.get('user_id'))

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
        user_info = self.decode_token(token)
        if not user_info:
            return []

        user_id = uuid.UUID(user_info.get('user_id'))

        async with self.db_session as session:
            query = select(TransactionModel).where(
                TransactionModel.user_id == user_id,
                TransactionModel.created_at.between(start, end)
            )
            result = await session.execute(query)
            transactions = result.scalars().all()

        return transactions
