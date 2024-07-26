import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

@pytest.fixture
def user_data():
    return {'first_name': 'Тест', 'last_name': 'Пользователь'}

@pytest.fixture
def transaction_data():
    return {'amount': 100, 'type': 'credit', 'user_id': str(uuid4())}

@pytest.fixture
def date_range():
    return {
        'start': '2023-01-01T00:00:00',
        'end': '2024-12-31T00:00:00'
    }

def test_create_transaction(user_data, transaction_data):
    response = client.post("/transaction/users/", json=user_data)
    assert response.status_code == 200
    user_id = response.json()

    print(f"Created user ID: {user_id}")  # Debugging output

    transaction_data["user_id"] = user_id
    response = client.post("/transaction/transactions/", json=transaction_data)

    print(f"Create transaction response: {response.json()}")  # Debugging output
    assert response.status_code == 200
    assert response.json() == {"detail": "Transaction created"}

def test_get_transactions_report(user_data, transaction_data, date_range):
    response = client.post("/transaction/users/", json=user_data)
    assert response.status_code == 200
    user_id = response.json()

    print(f"Created user ID: {user_id}")  # Debugging output

    transaction_data["user_id"] = user_id
    client.post("/transaction/transactions/", json=transaction_data)

    response = client.post("/transaction/transactions/report/", json={
        "start": date_range["start"],
        "end": date_range["end"],
        "user_id": user_id
    })

    print(f"Get transactions report response: {response.json()}")  # Debugging output
    assert response.status_code == 200
    assert "transactions" in response.json()
    assert len(response.json()["transactions"]) > 0

def test_invalid_user_transaction(transaction_data):
    invalid_user_id = str(uuid4())
    transaction_data["user_id"] = invalid_user_id

    print(f"Invalid user ID for transaction: {invalid_user_id}")  # Debugging output
    response = client.post("/transaction/transactions/", json=transaction_data)

    print(f"Invalid user transaction response: {response.json()}")  # Debugging output
    assert response.status_code == 400
    assert response.json() == {"detail": "User ID does not exist"}
