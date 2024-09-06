import pytest
import uuid
from src.app.services.transaction_service import TransactionService, TransactionType
from decouple import config
import jwt
from unittest.mock import Mock

SECRET_KEY = config('SECRET_KEY')

@pytest.fixture
def db_session():
    """Создает mock объект для db_session."""
    return Mock()

@pytest.fixture
def auth_service_url():
    """Возвращает фиктивный URL сервиса аутентификации."""
    return "http://fake-auth-service"

@pytest.fixture
def service(db_session, auth_service_url):
    """Создает экземпляр TransactionService для тестов."""
    return TransactionService(db_session, auth_service_url)

@pytest.fixture
def valid_token(mocker):
    """Генерирует валидный JWT-токен для тестов."""
    token_data = {"username": "test_user", "user_id": str(uuid.uuid4())}
    token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    mocker.patch("src.app.services.transaction_service.SECRET_KEY", SECRET_KEY)
    return token

@pytest.fixture
def invalid_token():
    """Генерирует невалидный JWT-токен для тестов."""
    return "invalid_token"

@pytest.mark.asyncio
async def test_decode_valid_token(service, valid_token):
    """Тестирует успешное декодирование валидного токена."""
    user_data = await service.decode_token(valid_token)
    assert user_data is not None
    assert user_data["username"] == "test_user"

@pytest.mark.asyncio
async def test_decode_invalid_token(service, invalid_token):
    """Тестирует декодирование невалидного токена."""
    user_data = await service.decode_token(invalid_token)
    assert user_data is None

@pytest.mark.asyncio
async def test_create_transaction(service, valid_token):
    """Тестирует создание транзакции."""
    amount = 100.0
    transaction_type = TransactionType.debit
    response = await service.create_transaction(valid_token, amount, transaction_type)

    assert "Transaction created for user" in response
    assert len(service.transactions) == 1
    transaction = service.transactions[0]
    assert transaction.amount == amount
    assert transaction.type == transaction_type
