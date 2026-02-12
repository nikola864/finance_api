from pydantic import BaseModel
from typing import Literal, List
from datetime import datetime

class TransactionTypeSchema(BaseModel):
    value: Literal["income", "expense"]
    display_name: str
    sign: str
    is_income: bool
    is_expense: bool

class CategoryTypeSchema(BaseModel):
    value: Literal["income", "expense"]
    display_name: str
    is_income: bool
    is_expense: bool

class BudgetPeriodSchema(BaseModel):
    value: Literal["daily", "weekly", "monthly", "yearly"]
    display_name: str
    days: int

class EnumResponse(BaseModel):
    transaction_types: List[TransactionTypeSchema]
    category_types: List[CategoryTypeSchema]
    budget_types: List[BudgetPeriodSchema]
