from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum


class TransactionType(str, Enum):

    INCOME = "income"
    EXPENSE = "expense"

    @property
    def display_name(self) -> str:
        return "Доход" if self == TransactionType.INCOME else "Расход"

    @property
    def sign(self) -> str:
        return "+" if self == TransactionType.INCOME else "-"

    @property
    def is_income(self) -> bool:
        return self == TransactionType.INCOME

    @property
    def is_expense(self) -> bool:
        return self == TransactionType.EXPENSE


class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

    @property
    def display_name(self) -> str:
        return "Доход" if self == CategoryType.INCOME else "Расход"

    @property
    def is_income(self) -> bool:
        return self == CategoryType.INCOME

    @property
    def is_expense(self) -> bool:
        return self == CategoryType.EXPENSE


class BudgetPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

    @property
    def display_name(self) -> str:
        names = {
            "daily": "Ежедневно",
            "weekly": "Еженедельно",
            "monthly": "Ежемесячно",
            "yearly": "Ежегодно"
        }
        return names[self.value]

    @property
    def days(self) -> int:
        days_map = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
            "yearly": 365
        }
        return days_map[self.value]


TransactionTypeEnum = SQLAlchemyEnum(TransactionType, name="transaction_type")
CategoryTypeEnum = SQLAlchemyEnum(CategoryType, name="category_type")
BudgetPeriodEnum = SQLAlchemyEnum(BudgetPeriod, name="budget_period")

