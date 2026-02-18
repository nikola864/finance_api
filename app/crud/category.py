from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.category import CategoryCreate, CategoryUpdate


async def create_category(
        db: AsyncSession,
        category: CategoryCreate,
        user_id: int
) -> Category:
    db_category = Category(
        name=category.name,
        type=category.type,
        color=category.color,
        icon=category.icon,
        is_default=category.is_default,
        user_id=user_id
    )
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def get_category(
        db: AsyncSession,
        category_id: int,
        user_id: int
) -> Category | None:
    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def get_categories(
        db: AsyncSession,
        user_id: int,
        category_type: str | None = None,
        skip: int = 0,
        limit: int = 100
):
    query = select(Category).where(Category.user_id == user_id)

    if category_type:
        query = query.where(Category.type == category_type)

    query = query.order_by(Category.name).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_category(
        db: AsyncSession,
        category_id: int,
        user_id: int,
        category_update: CategoryUpdate
) -> Category | None:
    query = (
        update(Category)
        .where(
            Category.id == category_id,
            Category.user_id == user_id
        )
        .values(**category_update.model_dump(exclude_unset=True))
        .returning(Category)
    )
    result = await db.execute(query)
    await db.commit()
    return result.scalar_one_or_none()


async def delete_category(
        db: AsyncSession,
        category_id: int,
        user_id: int
) -> bool:
    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.user_id == user_id
        )
    )
    category = result.scalar_one_or_none()
    if not category:
        return False
    await db.delete(category)
    await db.commit()
    return True


async def get_default_categories(
        db: AsyncSession,
        user_id: int
):
    result = await db.execute(
        select(Category).where(
            Category.user_id == user_id,
            Category.is_default == True
        )
    )
    return result.scalars().all()


async def get_category_statistics(
        db: AsyncSession,
        user_id: int,
        category_id: int,
        start_date: datetime,
        end_date: datetime
) -> dict:
    income = await db.execute(
        select(func.sum(Transaction.amount))
        .select_from(Transaction)
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "income",
            Transaction.category_id == category_id,
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        )
    )
    total_income = income.scalar() or Decimal('0.00')

    expense = await db.execute(
        select(func.sum(Transaction.amount))
        .join(Transaction)
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            Transaction.category_id == category_id,
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        )
    )
    total_expense = expense.scalar() or Decimal('0.00')

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": total_income - total_expense,
        "transaction_count": await db.scalar(
            select(func.count())
            .join(Transaction)
            .where(
                Transaction.user_id == user_id,
                Transaction.category_id == category_id,
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date
            )
        )
    }