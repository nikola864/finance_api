from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import category as category_crud
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead



class CategoryService:

    @staticmethod
    async def create_category(
            db: AsyncSession,
            user_id: int,
            category_data: CategoryCreate
    ) -> CategoryRead:
        db_category = await category_crud.create_category(db=db, category=category_data, user_id=user_id)
        return CategoryRead.model_validate(db_category)

    @staticmethod
    async def get_category(
            db: AsyncSession,
            user_id: int,
            category_id: int
    ) -> CategoryRead:
        category = await category_crud.get_category(db=db, category_id=category_id, user_id=user_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return CategoryRead.model_validate(category)

    @staticmethod
    async def get_categories(
            db: AsyncSession,
            user_id: int,
            category_type: str | None = None,
            skip: int = 0,
            limit: int = 100
    ) -> list[CategoryRead]:

        categories = await category_crud.get_categories(db, user_id, category_type, skip, limit)
        return [CategoryRead.model_validate(cat) for cat in categories]

    @staticmethod
    async def get_default_category(
            db: AsyncSession,
            user_id: int
    ) -> list[CategoryRead]:

        categories = await category_crud.get_default_categories(db, user_id)
        return [CategoryRead.model_validate(cat) for cat in categories]

    @staticmethod
    async def update_category(
            db: AsyncSession,
            user_id: int,
            category_id: int,
            update_data: CategoryUpdate
    ) -> CategoryRead:

        existing_category = await category_crud.get_category(db, category_id, user_id)
        if not existing_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        updated_category = await category_crud.update_category(db, category_id, user_id, update_data)
        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Couldn't update category"
            )

        return CategoryRead.model_validate(updated_category)

    @staticmethod
    async def delete_category(
            db: AsyncSession,
            category_id: int,
            user_id: int
    ) -> dict:

        existing_category = await category_crud.get_category(db, category_id, user_id)
        if not existing_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        success = await category_crud.delete_category(db, category_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Couldn't delete category"
            )

        return {"message": "The category was successfully deleted", "category_id": category_id}

    @staticmethod
    async def get_category_statistics(
            db: AsyncSession,
            user_id: int,
            category_id: int,
            start_date: str,
            end_date: str
    ) -> dict:

        category = await category_crud.get_category(db, category_id, user_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        from datetime import datetime, timezone

        start_dt = datetime.fromisoformat(start_date.replace("z", "+00:00")) if isinstance(start_date, str) else start_date
        end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00")) if isinstance(end_date, str) else end_date

        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)

        stats = await category_crud.get_category_statistics(
            db=db,
            user_id=user_id,
            category_id=category_id,
            start_date=start_dt,
            end_date=end_dt)

        return stats






































