import logging
from datetime import datetime
from fastapi import FastAPI
from src.app.routers import transaction
from src.app.services.transaction_service import TransactionService, TransactionType

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

transactions = [50, 100, 200]
date = [(2023, 1, 1), (2024, 12, 31)]
st = datetime(*date[0])
end = datetime(*date[1])

app = FastAPI()

@app.get("/")
def read_main():
    return {"message": "Welcome to the Transaction Service API"}

app.include_router(transaction.router, prefix="/transaction", tags=["transaction"])

# def main():
#     """Основная функция для запуска примера транзакций."""
#     service = TransactionService()
#     user_id = service.add_user('Алиса', 'Сокольникова')
#     logging.info(
#         'Создание транзакции для пользователя {0}'.format(
#             user_id,
#         ),
#     )
#     logging.info(
#         service.create_transaction(
#             user_id, transactions[0], TransactionType.credit,
#         ),
#     )
#     logging.info(
#         service.create_transaction(
#             user_id, transactions[1], TransactionType.debit,
#         ),
#     )
#     transactions_alice = service.get_user_transactions(
#         user_id, st, end,
#     )

#     logging.info(
#         'Транзакции пользователя {0} с {1} по {2}'.format(
#             user_id, st, end,
#         ),
#     )
#     for transaction in transactions_alice:
#         logging.info(transaction)

#     logging.info('Сохранение отчёта пользователя {0}'.format(user_id))
#     service.save_report(user_id, transactions_alice)
#     user_id = service.add_user('Боб', 'Власов')
#     logging.info(
#         'Создание транзакции для пользователя {0}'.format(user_id),
#         service.create_transaction(
#             user_id,
#             transactions[2],
#             TransactionType.credit,
#         ),
#     )

# if __name__ == '__main__':
#     main()
