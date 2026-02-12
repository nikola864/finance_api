from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, List
from .enum import CategoryTypeSchema
from .transaction import TransactionRead

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: Literal["income", "expense"] = "expense"
    color: Optional[str] = Field(None, pattern=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    icon: Optional[str] = Field(None, max_length=50)
    is_default: bool = False

class CategoryRead(BaseModel):
    id: int
    name: str
    type: str
    color: Optional[str] = None
    icon: Optional[str] = None
    is_default: bool
    user_id: int
    transactions_count: int = 0

    @property
    def is_income(self) -> bool:
        return self.type == "income"

    @property
    def is_expense(self) -> bool:
        return self.type == "expense"

    model_config = {
        "from_attributes": True
    }

class CategoryReadWithTransactions(CategoryRead):
    transactions: List[TransactionRead] = []


