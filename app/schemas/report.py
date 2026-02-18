from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import List

class TransactionStatistics(BaseModel):
    total_count: int
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
    average_transaction: Decimal
    period_start: datetime
    period_end: datetime

class BudgetStatistics(BaseModel):
    total_budgets: int
    active_budgets: int
    total_amount: Decimal
    average_amount: Decimal

class FinancialSummary(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
    last_30_days_income: Decimal
    last_30_days_expense: Decimal
    top_categories: List[dict]