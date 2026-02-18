from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionFilter
from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple, List


async def create_transaction(
        db: AsyncSession,
        transaction_data: dict
) -> Transaction:
    """
    Создание новой транзакции.

    Args:
        db: Асинхронная сессия базы данных
        transaction_data: Словарь с данными транзакции

    Returns:
        Созданная транзакция
    """
    db_transaction = Transaction(**transaction_data)
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction


async def get_transaction_by_id(
        db: AsyncSession,
        transaction_id: int
) -> Transaction | None:
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    return result.scalar_one_or_none()


async def get_transactions(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[TransactionFilter] = None
) -> Tuple[List[Transaction], int]:

    # Строим запрос для получения транзакций
    query = select(Transaction).where(Transaction.user_id == user_id)

    # Применяем фильтры
    if filters:
        query = apply_filters(query, filters)

    # Применяем пагинацию и сортировку
    query = query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit)

    # Выполняем запрос
    result = await db.execute(query)
    transactions = result.scalars().all()

    # Считаем общее количество для пагинации
    total = await count_transactions(db, user_id, filters)

    return transactions, total


def apply_filters(query: Select, filters: TransactionFilter) -> Select:

    filter_dict = filters.model_dump(exclude_unset=True)

    # Фильтр по типу транзакции
    if "transaction_type" in filter_dict and filter_dict["transaction_type"] is not None:
        query = query.where(Transaction.transaction_type == filter_dict["transaction_type"])

    # Фильтр по категории
    if "category_id" in filter_dict and filter_dict["category_id"] is not None:
        query = query.where(Transaction.category_id == filter_dict["category_id"])

    # Фильтр по дате начала
    if "start_date" in filter_dict and filter_dict["start_date"] is not None:
        query = query.where(Transaction.created_at >= filter_dict["start_date"])

    # Фильтр по дате окончания
    if "end_date" in filter_dict and filter_dict["end_date"] is not None:
        query = query.where(Transaction.created_at <= filter_dict["end_date"])

    # Фильтр по минимальной сумме
    if "min_amount" in filter_dict and filter_dict["min_amount"] is not None:
        query = query.where(Transaction.amount >= filter_dict["min_amount"])

    # Фильтр по максимальной сумме
    if "max_amount" in filter_dict and filter_dict["max_amount"] is not None:
        query = query.where(Transaction.amount <= filter_dict["max_amount"])

    # Поиск по описанию
    if "search" in filter_dict and filter_dict["search"] is not None:
        search_term = f"%{filter_dict['search'].lower()}%"
        query = query.where(Transaction.description.ilike(search_term))

    return query


async def count_transactions(
        db: AsyncSession,
        user_id: int,
        filters: Optional[TransactionFilter] = None
) -> int:
    """
    Подсчет общего количества транзакций с фильтрами.

    Args:
        db: Асинхронная сессия базы данных
        user_id: ID пользователя
        filters: Фильтры

    Returns:
        Общее количество транзакций
    """
    query = select(func.count()).select_from(Transaction).where(Transaction.user_id == user_id)

    if filters:
        query = apply_filters(query, filters)

    result = await db.execute(query)
    return result.scalar() or 0


async def update_transaction(
        db: AsyncSession,
        transaction_id: int,
        update_data: dict
) -> Transaction | None:
    """
    Обновление транзакции.

    Args:
        db: Асинхронная сессия базы данных
        transaction_id: ID транзакции
        update_data: Словарь с данными для обновления

    Returns:
        Обновленная транзакция или None
    """
    query = (
        update(Transaction)
        .where(Transaction.id == transaction_id)
        .values(**update_data, updated_at=datetime.now())
        .returning(Transaction)
    )
    result = await db.execute(query)
    await db.commit()
    return result.scalar_one_or_none()


async def delete_transaction(
        db: AsyncSession,
        transaction_id: int
) -> bool:
    """
    Удаление транзакции.

    Args:
        db: Асинхронная сессия базы данных
        transaction_id: ID транзакции

    Returns:
        True если удалено успешно, иначе False
    """
    result = await db.execute(
        delete(Transaction).where(Transaction.id == transaction_id)
    )
    await db.commit()
    return result.rowcount > 0


async def get_transaction_statistics(
        db: AsyncSession,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> dict:
    """
    Получение статистики по транзакциям.

    Args:
        db: Асинхронная сессия базы данных
        user_id: ID пользователя
        start_date: Начальная дата (опционально)
        end_date: Конечная дата (опционально)

    Returns:
        Словарь со статистикой
    """
    # Базовый запрос с фильтром по пользователю
    base_query = select(Transaction).where(Transaction.user_id == user_id)

    # Применяем фильтры по дате
    if start_date:
        base_query = base_query.where(Transaction.created_at >= start_date)
    if end_date:
        base_query = base_query.where(Transaction.created_at <= end_date)

    # Получаем все транзакции для расчета
    result = await db.execute(base_query)
    transactions = result.scalars().all()

    # Рассчитываем статистику
    total_count = len(transactions)
    total_income = sum(t.amount for t in transactions if t.transaction_type == "income")
    total_expense = sum(t.amount for t in transactions if t.transaction_type == "expense")
    balance = total_income - total_expense

    # Средние значения
    avg_transaction = (total_income + total_expense) / total_count if total_count > 0 else Decimal("0")

    income_transactions = [t for t in transactions if t.transaction_type == "income"]
    avg_income = total_income / len(income_transactions) if income_transactions else Decimal("0")

    expense_transactions = [t for t in transactions if t.transaction_type == "expense"]
    avg_expense = total_expense / len(expense_transactions) if expense_transactions else Decimal("0")

    return {
        "total_count": total_count,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "average_transaction": avg_transaction,
        "average_income": avg_income,
        "average_expense": avg_expense
    }