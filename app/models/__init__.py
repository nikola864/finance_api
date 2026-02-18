# models/__init__.py
"""
Инициализация всех моделей для регистрации в Base.metadata.

ВАЖНО: Импортируем модели в правильном порядке, чтобы избежать циклических зависимостей.
"""

from .base import Base

# Сначала импортируем модели без внешних зависимостей
from .user import User
from .category import Category

# Затем импортируем модели, которые ссылаются на другие модели
from .transaction import Transaction
from .budget import Budget  # Если есть

# Если есть ассоциативные таблицы
try:
    from .transaction_category import transaction_categories
except ImportError:
    pass

__all__ = [
    "Base",
    "User",
    "Category",
    "Transaction",
    "Budget"
]