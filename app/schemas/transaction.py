from pydantic import BaseModel, Field, computed_field
from decimal import Decimal
from typing import Optional, Literal
from datetime import datetime

class TransactionCreate(BaseModel):
    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Сумма транзакции (больше 0)"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Описание транзакции"
    )
    transaction_type: Literal["income", "expense"] = Field(
        default="expense",
        description="Тип транзакции: income или expense"
    )
    category_id: Optional[int] = Field(
        None,
        description="ID категории (опционально)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": "1500.50",
                "description": "Зарплата за февраль",
                "transaction_type": "income",
                "category_id": 1
            }
        }
    }


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = Field(
        None,
        gt=0,
        decimal_places=2,
        description="Новая сумма транзакции"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Новое описание транзакции"
    )
    transaction_type: Optional[Literal["income", "expense"]] = Field(
        None,
        description="Новый тип транзакции"
    )
    category_id: Optional[int] = Field(
        None,
        description="Новый ID категории"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": "1600.00",
                "description": "Исправленная зарплата",
                "transaction_type": "income"
            }
        }
    }


class TransactionRead(BaseModel):
    id: int = Field(..., description="ID транзакции")
    amount: Decimal = Field(..., decimal_places=2, description="Сумма транзакции")
    description: Optional[str] = Field(None, description="Описание транзакции")
    transaction_type: str = Field(..., description="Тип транзакции (income/expense)")
    user_id: int = Field(..., description="ID пользователя")
    category_id: Optional[int] = Field(None, description="ID категории")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего обновления")

    @computed_field
    @property
    def is_income(self) -> bool:
        """Является ли транзакция доходом"""
        return self.transaction_type == "income"

    @computed_field
    @property
    def is_expense(self) -> bool:
        """Является ли транзакция расходом"""
        return self.transaction_type == "expense"

    @computed_field
    @property
    def sign(self) -> str:
        """Знак транзакции (+ для дохода, - для расхода)"""
        return "+" if self.is_income else "-"

    @computed_field
    @property
    def signed_amount(self) -> Decimal:
        """Сумма с учетом знака"""
        return self.amount if self.is_income else -self.amount

    @computed_field
    @property
    def display_type(self) -> str:
        """Человекочитаемый тип транзакции"""
        return "Доход" if self.is_income else "Расход"

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "amount": "1500.50",
                "description": "Зарплата за февраль",
                "transaction_type": "income",
                "user_id": 1,
                "category_id": 1,
                "created_at": "2026-02-12T10:00:00Z",
                "updated_at": "2026-02-12T10:00:00Z",
                "is_income": True,
                "is_expense": False,
                "sign": "+",
                "signed_amount": "1500.50",
                "display_type": "Доход"
            }
        }
    }

class TransactionFilter(BaseModel):
    start_date: Optional[datetime] = Field(None, description="Начальная дата для фильтрации")
    end_data: Optional[datetime] = Field(None, description="Конечная дата для фильтрации")
    transaction_type: Optional[Literal["income", "expense"]] = Field(None, description="Тип транзакции для фильтрации")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="Минимальная сумма")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="Максимальная сумма")
    category_id: Optional[int] = Field(None, description="ID категории для фильтрации")
    search: Optional[str] = Field(None, max_length=100, description="Поиск по описанию")

    model_config = {
        "json_schema_extra": {
            "example": {
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-01-31T23:59:59Z",
                "transaction_type": "expense",
                "min_amount": "100.00",
                "max_amount": "5000.00",
                "category_id": 1,
                "search": "продукты"
            }
        }
    }

class TransactionStatistics(BaseModel):
    total_count: int = Field(..., description="Общее количество транзакции")
    total_income: Decimal = Field(..., decimal_places=2, description="Общая сумма доходов")
    total_expense: Decimal = Field(..., decimal_places=2, description="Общая сумма расходов")
    balance: Decimal = Field(..., decimal_places=2, description="Баланс (доходы - расходы)")
    average_transaction: Decimal = Field(..., decimal_places=2, description="Средняя сумма транзакций")
    average_income: Decimal = Field(..., decimal_places=2, description="Средняя сумма доходов")
    average_expense: Decimal = Field(..., decimal_places=2, description="Средняя сумма расходов")
    period_start: Optional[datetime] = Field(None, description="Начало периода")
    period_end: Optional[datetime] = Field(None, description="Конец периода")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_count": 42,
                "total_income": "50000.00",
                "total_expense": "30000.00",
                "balance": "20000.00",
                "average_transaction": "1190.48",
                "average_income": "12500.00",
                "average_expense": "3000.00",
                "period_start": "2026-01-01T00:00:00Z",
                "period_end": "2026-01-31T23:59:59Z"
            }
        }
    }


class TransactionReadWithCategory(TransactionRead):
    category: Optional["CategoryRead"] = Field(
        None,
        description="Полная информация о категории"
    )

    model_config = {
        "from_attributes": True
    }

from .category import CategoryRead
TransactionReadWithCategory.model_rebuild()

TransactionResponse = TransactionReadWithCategory