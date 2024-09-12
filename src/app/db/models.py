import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, String
from sqlalchemy.dialects.postgresql import UUID

from src.app.db.db import Base

class TransactionModel(Base):
    """Модель для транзакций."""

    __tablename__ = 'transactions'
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id = Column(UUID(as_uuid=True), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Преобразование модели в словарь для сериализации."""
        return {
            "id": str(self.id),  # Преобразуем UUID в строку
            "user_id": str(self.user_id),  # Преобразуем UUID в строку
            "amount": self.amount,
            "type": self.type,
            "created_at": self.created_at.isoformat(),  # Преобразуем datetime в строку
        }
