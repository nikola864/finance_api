from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from decimal import Decimal
from app.crud import transaction as transaction_crud
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionReadWithCategory,
    TransactionFilter,
    TransactionStatistics as TransactionStatsSchema
)


class TransactionService:

    @staticmethod
    async def create_transaction(
            db: AsyncSession,
            user_id: int,
            transaction_data: TransactionCreate
    ) -> TransactionReadWithCategory:

        transaction_dict = transaction_data.model_dump()
        transaction_dict["user_id"] = user_id

        db_transaction = await transaction_crud.create_transaction(db, transaction_data=transaction_dict)
        return TransactionReadWithCategory.model_validate(db_transaction)

    @staticmethod
    async def get_transaction(
            db: AsyncSession,
            user_id: int,
            transaction_id: int
    ) -> TransactionReadWithCategory:

        transaction = await transaction_crud.get_transaction_by_id(db, transaction_id)
        if not transaction or transaction.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        return TransactionReadWithCategory.model_validate(transaction)

    @staticmethod
    async def get_transactions(
            db: AsyncSession,
            user_id: int,
            skip: int = 0,
            limit: int = 100,
            filters: TransactionFilter | None = None
    ) -> tuple[list[TransactionReadWithCategory], int, int]:

        transactions, total = await transaction_crud.get_transactions(db, user_id, skip, limit, filters)
        page = skip // limit + 1 if limit > 0 else 1

        return (
            [TransactionReadWithCategory.model_validate(t) for t in transactions],
            total,
            page
        )

    @staticmethod
    async def update_transaction(
            db: AsyncSession,
            user_id: int,
            transaction_id: int,
            update_data: TransactionUpdate
    ) -> TransactionReadWithCategory:

        transaction = await transaction_crud.get_transaction_by_id(db, transaction_id)
        if not transaction or transaction.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )

        update_dict = update_data.model_dump(exclude_unset=True)

        updated_transaction = await transaction_crud.update_transaction(
            db, transaction_id, update_data=update_dict
        )
        if not updated_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Couldn't update transaction"
            )

        return TransactionReadWithCategory.model_validate(updated_transaction)

    @staticmethod
    async def delete_transaction(
            db: AsyncSession,
            user_id: int,
            transaction_id: int
    ) -> dict:

        transaction = await transaction_crud.get_transaction_by_id(db, transaction_id)
        if not transaction or transaction.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        success = await transaction_crud.delete_transaction(db, transaction_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Couldn't delete transaction"
            )
        return {"message": "The transaction was successfully deleted", "transaction_id": transaction_id}

    @staticmethod
    async def get_transaction_statistics(
            db: AsyncSession,
            user_id: int,
            start_date: str | None = None,
            end_date: str | None = None,
    ) -> TransactionStatsSchema:

        start_dt = None
        end_dt = None

        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=timezone.utc)

        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            if end_dt.tzinfo is None:
                end_dt = end_dt.replace(tzinfo=timezone.utc)

        stats = await transaction_crud.get_transaction_statistics(
            db=db,
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt
        )

        return TransactionStatsSchema(
            total_count=stats["total_count"],
            total_income=stats["total_income"],
            total_expense=stats["total_expense"],
            balance=stats["balance"],
            average_transaction=stats["average_transaction"],
            average_income=stats["average_income"],
            average_expense=stats["average_expense"],
            period_start=start_dt,
            period_end=end_dt
        )
















