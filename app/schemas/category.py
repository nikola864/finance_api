from pydantic import BaseModel, Field
from typing import Optional, Literal, List


class CategoryCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название категории"
    )
    type: Literal["income", "expense"] = Field(
        default="expense",
        description="Тип категории: income или expense"
    )
    color: Optional[str] = Field(
        None,
        pattern=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        description="Цвет в формате HEX (#RRGGBB или #RGB)"
    )
    icon: Optional[str] = Field(
        None,
        max_length=50,
        description="Иконка категории (например, emoji или имя иконки)"
    )
    is_default: bool = Field(
        default=False,
        description="Является ли категорией по умолчанию"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Продукты",
                "type": "expense",
                "color": "#FF6B6B",
                "icon": "🛒",
                "is_default": False
            }
        }
    }


class CategoryUpdate(BaseModel):
    """Схема для обновления категории (все поля опциональны)"""
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Новое название категории"
    )
    type: Optional[Literal["income", "expense"]] = Field(
        None,
        description="Новый тип категории"
    )
    color: Optional[str] = Field(
        None,
        pattern=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        description="Новый цвет в формате HEX"
    )
    icon: Optional[str] = Field(
        None,
        max_length=50,
        description="Новая иконка категории"
    )
    is_default: Optional[bool] = Field(
        None,
        description="Новый статус категории по умолчанию"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Супермаркет",
                "color": "#4ECDC4",
                "icon": "🏪"
            }
        }
    }


class CategoryRead(BaseModel):
    """Схема для чтения категории"""
    id: int = Field(..., description="ID категории")
    name: str = Field(..., description="Название категории")
    type: str = Field(..., description="Тип категории (income/expense)")
    color: Optional[str] = Field(None, description="Цвет категории")
    icon: Optional[str] = Field(None, description="Иконка категории")
    is_default: bool = Field(..., description="Является ли категорией по умолчанию")
    user_id: int = Field(..., description="ID владельца категории")
    transactions_count: int = Field(
        default=0,
        description="Количество транзакций в этой категории"
    )

    @property
    def is_income(self) -> bool:
        """Является ли категория доходом"""
        return self.type == "income"

    @property
    def is_expense(self) -> bool:
        """Является ли категория расходом"""
        return self.type == "expense"

    @property
    def display_type(self) -> str:
        """Человекочитаемый тип категории"""
        return "Доход" if self.is_income else "Расход"

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Продукты",
                "type": "expense",
                "color": "#FF6B6B",
                "icon": "🛒",
                "is_default": False,
                "user_id": 1,
                "transactions_count": 15,
                "is_income": False,
                "is_expense": True,
                "display_type": "Расход"
            }
        }
    }


class CategoryReadWithTransactions(CategoryRead):
    """Схема для чтения категории с транзакциями"""
    transactions: List["TransactionRead"] = Field(
        default_factory=list,
        description="Список транзакций в этой категории"
    )

    model_config = {
        "from_attributes": True
    }

from .transaction import TransactionRead
CategoryReadWithTransactions.model_rebuild()