# main.py

import logging
from datetime import datetime
from app.transaction import TransactionService, TransactionType

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)


def main():
    service = TransactionService()

    # Добавление пользователей
    user_id_alice = service.add_user("Алиса", "Сокольникова")
    user_id_bob = service.add_user("Боб", "Власов")

    # Создание транзакций для пользователя Алиса
    logging.info(f"Создание транзакции для пользователя {user_id_alice}")
    logging.info(service.create_transaction(
        user_id_alice, 100, TransactionType.CREDIT))
    logging.info(service.create_transaction(
        user_id_alice, 50, TransactionType.DEBIT))

    # Создание транзакций для пользователя Боба
    logging.info(f"Creating transactions for user {user_id_bob}")
    logging.info(service.create_transaction(
        user_id_bob, 200, TransactionType.CREDIT))

    # Получение и вывод транзакций для пользователя Алиса за все время
    start_time = datetime(2023, 1, 1)
    end_time = datetime(2024, 12, 31)
    transactions_alice = service.get_transactions(
        user_id_alice, start_time, end_time)

    logging.info(f"Transactions for user {user_id_alice} from {
                 start_time} to {end_time}")
    for transaction in transactions_alice:
        logging.info(transaction)
    logging.info("")  # Empty line for separation

    # Сохранение и вывод отчета для пользователя Алиса
    logging.info(f"Saving report for user {user_id_alice}")
    service.save_report(user_id_alice, transactions_alice)


if __name__ == "__main__":
    main()
