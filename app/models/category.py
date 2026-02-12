from typing import TYPE_CHECKING, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Index
from app.models.base import Base
from app.models.enums import CategoryType, CategoryTypeEnum

if TYPE_CHECKING:
    from .user import User
    from .transaction import Transaction
    from .budget import Budget

class Category(Base):

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    type: Mapped[CategoryType] = mapped_column(
        CategoryTypeEnum,
        nullable=False,
        index=True,
        default=CategoryType.EXPENSE
    )

    color: Mapped[str | None] = mapped_column(String(20), default=None)
    icon: Mapped[str | None] = mapped_column(String(50), default=None)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    user: Mapped["User"] = relationship(back_populates="categories")
    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    budgets: Mapped[List["Budget"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    __table_args__ = (
        Index('ix_category_user_type', 'user_id', 'type'),
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', type={self.type.value})>"

    def __str__(self) -> str:
        return self.name

    @property
    def is_income(self) -> bool:
        """Проверка, является ли категория доходом"""
        return self.type == CategoryType.INCOME

    @property
    def is_expense(self) -> bool:
        """Проверка, является ли категория расходом"""
        return self.type == CategoryType.EXPENSE

    @property
    def display_type(self) -> str:
        """Человекочитаемый тип категории"""
        return self.type.display_name