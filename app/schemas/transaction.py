from pydantic import BaseModel, Field, computed_field
from decimal import Decimal
from typing import Optional, Literal
from datetime import datetime
from .enum import TransactionTypeSchema
from .category import CategoryRead

class TransactionCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: Optional[str] = Field(None, max_length=500)
    transaction_type: Literal["income", "expense"] = "expense"
    category_id: Optional[int] = None

class TransactionRead(BaseModel):
    id: int
    amount: Decimal
    description: Optional[str] = None
    transaction_type: str
    user_id: int
    category_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def is_income(self) -> bool:
        return self.transaction_type == "income"

    @computed_field
    @property
    def is_expense(self) -> bool:
        return self.transaction_type == "expense"

    @computed_field
    @property
    def sign(self) -> str:
        return "+" if self.is_income else "-"

    @computed_field
    @property
    def signed_amount(self) -> Decimal:
        return self.amount if self.is_income else -self.amount

    @computed_field
    @property
    def display_type(self) -> str:
        return "Доход" if self.is_income else "Расход"

    model_config = {
        "from_attributes": True
    }

class TransactionReadWithCategory(TransactionRead):
    category: Optional[CategoryRead] = None























