from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Index
from datetime import datetime, timezone
from app.models.base import Base
from app.models.enums import BudgetPeriod, BudgetPeriodEnum

if TYPE_CHECKING:
    from .user import User
    from .category import Category


class Budget(Base):
    """
    Модель бюджета с использованием Enum для периодов.
    """

    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)

    # Используем Enum вместо строки
    period: Mapped[BudgetPeriod] = mapped_column(
        BudgetPeriodEnum,
        nullable=False,
        index=True,
        default=BudgetPeriod.MONTHLY
    )

    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="budgets")
    category: Mapped["Category"] = relationship(back_populates="budgets")

    __table_args__ = (
        Index('ix_budget_user_period', 'user_id', 'period'),
        Index('ix_budget_active', 'user_id', 'start_date', 'end_date'),
    )

    def __repr__(self) -> str:
        return f"<Budget(id={self.id}, name='{self.name}', amount={self.amount})>"

    def __str__(self) -> str:
        return self.name

    @property
    def is_active(self) -> bool:
        """Проверка, активен ли бюджет сейчас"""
        now = datetime.now(timezone.utc)
        return self.start_date <= now <= self.end_date

    @property
    def duration_days(self) -> int:
        """Длительность бюджета в днях"""
        return (self.end_date - self.start_date).days

    @property
    def display_period(self) -> str:
        """Человекочитаемый период"""
        return self.period.display_name