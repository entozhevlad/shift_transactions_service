import pytest
import uuid
from datetime import datetime, timedelta
from src.app.transaction import User, TransactionType, Transaction, Report, TransactionService

@pytest.fixture
def transaction_service():
    return TransactionService()

@pytest.fixture
def user_id(transaction_service):
    return transaction_service.add_user("John", "Doe")

@pytest.fixture
def transactions(transaction_service, user_id):
    now = datetime.now()
    transactions = [
        Transaction(user_id=user_id, amount=100, type=TransactionType.CREDIT, time=now - timedelta(days=1)),
        Transaction(user_id=user_id, amount=50, type=TransactionType.DEBIT, time=now - timedelta(days=2)),
        Transaction(user_id=user_id, amount=200, type=TransactionType.CREDIT, time=now - timedelta(days=3))
    ]
    transaction_service.transactions.extend(transactions)
    return transactions

def test_add_user(transaction_service):
    user_id = transaction_service.add_user("Jane", "Doe")
    assert user_id in transaction_service.users
    assert transaction_service.users[user_id].first_name == "Jane"
    assert transaction_service.users[user_id].last_name == "Doe"

def test_create_transaction(transaction_service, user_id):
    transaction_service.create_transaction(user_id, 150, TransactionType.CREDIT)
    assert len(transaction_service.transactions) == 1
    assert transaction_service.transactions[0].amount == 150
    assert transaction_service.transactions[0].type == TransactionType.CREDIT

def test_create_transaction_user_not_found(transaction_service):
    non_existent_user_id = uuid.uuid4()
    with pytest.raises(ValueError):
        transaction_service.create_transaction(non_existent_user_id, 150, TransactionType.CREDIT)

def test_get_transactions(transaction_service, user_id, transactions):
    now = datetime.now()
    start = now - timedelta(days=4)
    end = now
    result = transaction_service.get_transactions(user_id, start, end)
    assert len(result) == 3
    assert result[0].amount == 100
    assert result[1].amount == 50
    assert result[2].amount == 200

def test_get_transactions_user_not_found(transaction_service):
    non_existent_user_id = uuid.uuid4()
    start = datetime.now() - timedelta(days=4)
    end = datetime.now()
    with pytest.raises(ValueError):
        transaction_service.get_transactions(non_existent_user_id, start, end)

def test_save_report(transaction_service, user_id, transactions):
    transaction_service.save_report(user_id, transactions)
    assert len(transaction_service.reports) == 1
    assert transaction_service.reports[0].user_id == user_id
    assert len(transaction_service.reports[0].transactions) == 3

@pytest.mark.parametrize("first_name,last_name", [
    ("Alice", "Wonderland"),
    ("Bob", "Builder"),
    ("Charlie", "Chocolate")
])
def test_add_multiple_users(transaction_service, first_name, last_name):
    user_id = transaction_service.add_user(first_name, last_name)
    assert user_id in transaction_service.users
    assert transaction_service.users[user_id].first_name == first_name
    assert transaction_service.users[user_id].last_name == last_name
