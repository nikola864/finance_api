from pydantic import BaseModel, Field, computed_field, field_validator
from decimal import Decimal
from typing import Optional, Literal
from datetime import datetime, timezone
from .category import CategoryRead


class BudgetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    period: Literal["daily", "weekly", "monthly", "yearly"] = "monthly"
    start_date: datetime
    end_date: datetime
    category_id: int

    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_timezone(cls, v):
        if v.tzinfo is None:
            raise ValueError('Дата должна содержать информацию о часовом поясе')
        return v

    @field_validator('end_date')
    @classmethod
    def end_date_after_start_date(cls, v, info):
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('Дата окончания должна быть позже даты начала')
        return v


class BudgetRead(BaseModel):
    id: int
    name: str
    amount: Decimal
    period: str
    start_date: datetime
    end_date: datetime
    user_id: int
    category_id: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def is_active(self) -> bool:
        now = datetime.now(timezone.utc)
        return self.start_date <= now <= self.end_date

    @computed_field
    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days

    @computed_field
    @property
    def display_period(self) -> str:
        return {
            "daily": "Ежедневно",
            "weekly": "Еженедельно",
            "monthly": "Ежемесячно",
            "yearly": "Ежегодно"
        }.get(self.period, self.period)

    @computed_field
    @property
    def days_remaining(self) -> int:
        now = datetime.now(timezone.utc)
        if now > self.end_date:
            return 0
        return (self.end_date - now).days

    @computed_field
    @property
    def progress(self) -> float:
        now = datetime.now(timezone.utc)
        if now < self.start_date:
            return 0.0
        if now > self.end_date:
            return 100.0
        total_days = (self.end_date - self.start_date).days
        elapsed_days = (now - self.start_date).days
        return round((elapsed_days / total_days) * 100, 2) if total_days > 0 else 0.0

    model_config = {
        "from_attributes": True
    }


class BudgetReadWithCategory(BudgetRead):
    category: Optional[CategoryRead] = None