from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Text, Index
from datetime import datetime, timezone
from app.models.base import Base
from app.models.enums import TransactionType, TransactionTypeEnum

if TYPE_CHECKING:
    from .user import User
    from .category import Category

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    amount: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    transaction_type: Mapped[TransactionType] = mapped_column(
        TransactionTypeEnum,
        nullable=False,
        index=True,
        default=TransactionType.EXPENSE
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), default=None, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="transactions")
    category: Mapped["Category | None"] = relationship(back_populates="transactions")

    __table_args__ = (
        Index('ix_transaction_user_type_date', 'user_id', 'transaction_type', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, amount={self.amount}, type={self.transaction_type.value})>"

    def __str__(self) -> str:
        return f"{self.transaction_type.display_name}: {self.amount}"

    @property
    def is_income(self) -> bool:
        """Проверка, является ли транзакция доходом"""
        return self.transaction_type == TransactionType.INCOME

    @property
    def is_expense(self) -> bool:
        """Проверка, является ли транзакция расходом"""
        return self.transaction_type == TransactionType.EXPENSE

    @property
    def signed_amount(self) -> float:
        """Сумма с учетом знака (+ для дохода, - для расхода)"""
        return self.amount if self.is_income else -self.amount