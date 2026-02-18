from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.category import Category
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List


async def get_daily_report(
        db: AsyncSession,
        user_id: int,
        date: datetime | None = None
) -> Dict:
    if not date:
        date = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    tomorrow = date + timedelta(days=1)

    return await _get_period_report(
        db,
        user_id,
        date,
        tomorrow,
        "daily"
    )


async def get_weekly_report(
        db: AsyncSession,
        user_id: int,
        week_start: datetime | None = None
) -> Dict:
    if not week_start:
        today = datetime.now(timezone.utc)
        week_start = today - timedelta(days=today.weekday())

    week_end = week_start + timedelta(days=7)

    return await _get_period_report(
        db,
        user_id,
        week_start,
        week_end,
        "weekly"
    )


async def get_monthly_report(
        db: AsyncSession,
        user_id: int,
        month: datetime | None = None
) -> Dict:
    if not month:
        today = datetime.now(timezone.utc)
        month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    next_month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)

    return await _get_period_report(
        db,
        user_id,
        month,
        next_month,
        "monthly"
    )


async def get_custom_report(
        db: AsyncSession,
        user_id: int,
        start_date: datetime,
        end_date: datetime
) -> Dict:
    return await _get_period_report(
        db,
        user_id,
        start_date,
        end_date,
        "custom"
    )


async def _get_period_report(
        db: AsyncSession,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        period_type: str
) -> Dict:
    stats = await _get_transaction_statistics(
        db, user_id, start_date, end_date
    )

    categories = await _get_category_expenses(
        db, user_id, start_date, end_date
    )

    budgets = await _get_budget_status(
        db, user_id, start_date, end_date
    )

    return {
        "period_type": period_type,
        "start_date": start_date,
        "end_date": end_date,
        "total_income": stats["total_income"],
        "total_expense": stats["total_expense"],
        "net_balance": stats["net_balance"],
        "transaction_count": stats["transaction_count"],
        "categories": categories,
        "budgets": budgets
    }


async def _get_transaction_statistics(
        db: AsyncSession,
        user_id: int,
        start_date: datetime,
        end_date: datetime
) -> Dict:
    income = await db.scalar(
        select(func.sum(Transaction.amount))
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "income",
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        )
    )
    total_income = income or Decimal('0.00')

    expense = await db.scalar(
        select(func.sum(Transaction.amount))
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        )
    )
    total_expense = expense or Decimal('0.00')

    transaction_count = await db.scalar(
        select(func.count())
        .where(
            Transaction.user_id == user_id,
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        )
    )

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": total_income - total_expense,
        "transaction_count": transaction_count or 0
    }


async def _get_category_expenses(
        db: AsyncSession,
        user_id: int,
        start_date: datetime,
        end_date: datetime
) -> List[Dict]:
    result = await db.execute(
        select(
            Category.id,
            Category.name,
            Category.color,
            Category.icon,
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('transaction_count')
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date,
            Category.id == Transaction.category_id
        )
        .group_by(Category.id, Category.name, Category.color, Category.icon)
        .order_by(func.sum(Transaction.amount).desc())
    )

    return [
        {
            "id": row.id,
            "name": row.name,
            "color": row.color,
            "icon": row.icon,
            "total_amount": row.total_amount,
            "transaction_count": row.transaction_count
        }
        for row in result
    ]


async def _get_budget_status(
        db: AsyncSession,
        user_id: int,
        start_date: datetime,
        end_date: datetime
) -> List[Dict]:
    result = await db.execute(
        select(
            Budget.id,
            Budget.name,
            Budget.amount,
            Budget.period,
            Budget.start_date,
            Budget.end_date,
            Category.name.label('category_name'),
            Category.color,
            Category.icon
        )
        .join(Category, Budget.category_id == Category.id)
        .where(
            Budget.user_id == user_id,
            Budget.start_date <= end_date,
            Budget.end_date >= start_date
        )
    )

    budgets = []
    for budget in result:
        used_amount = await db.scalar(
            select(func.sum(Transaction.amount))
            .where(
                Transaction.user_id == user_id,
                Transaction.category_id == budget.category_id,
                Transaction.transaction_type == "expense",
                Transaction.created_at >= budget.start_date,
                Transaction.created_at <= budget.end_date
            )
        )
        used_amount = used_amount or Decimal('0.00')

        total_days = (budget.end_date - budget.start_date).days
        elapsed_days = (datetime.now(timezone.utc) - budget.start_date).days
        progress = min(100, max(0, (elapsed_days / total_days) * 100)) if total_days > 0 else 0

        budgets.append({
            "id": budget.id,
            "name": budget.name,
            "amount": budget.amount,
            "period": budget.period,
            "start_date": budget.start_date,
            "end_date": budget.end_date,
            "category": {
                "name": budget.category_name,
                "color": budget.color,
                "icon": budget.icon
            },
            "used_amount": used_amount,
            "remaining_amount": budget.amount - used_amount,
            "progress": round(progress, 2)
        })

    return budgets


async def get_statistics(
        db: AsyncSession,
        user_id: int
) -> Dict:
    stats = await _get_transaction_statistics(
        db,
        user_id,
        datetime.min.replace(tzinfo=timezone.utc),
        datetime.max.replace(tzinfo=timezone.utc)
    )

    today = datetime.now(timezone.utc)
    period_stats = {
        "today": await _get_transaction_statistics(db, user_id, today, today + timedelta(days=1)),
        "this_week": await _get_transaction_statistics(
            db,
            user_id,
            today - timedelta(days=today.weekday()),
            today + timedelta(days=7 - today.weekday())
        ),
        "this_month": await _get_transaction_statistics(
            db,
            user_id,
            today.replace(day=1),
            (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        ),
        "all_time": stats
    }

    top_categories = await _get_category_expenses(
        db,
        user_id,
        datetime.min.replace(tzinfo=timezone.utc),
        datetime.max.replace(tzinfo=timezone.utc)
    )

    return {
        "total_income": stats["total_income"],
        "total_expense": stats["total_expense"],
        "net_balance": stats["net_balance"],
        "transaction_count": stats["transaction_count"],
        "period_stats": period_stats,
        "top_categories": top_categories[:5]
    }