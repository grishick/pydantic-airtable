"""
Pydantic AirTable - A library for managing AirTable data using Pydantic objects
"""

from .base import AirTableModel, AirTableConfig
from .client import AirTableClient
from .fields import AirTableField
from .exceptions import AirTableError, RecordNotFoundError, ValidationError
from .base_manager import BaseManager
from .table_manager import TableManager

__version__ = "0.2.0"
__all__ = [
    "AirTableModel",
    "AirTableConfig", 
    "AirTableClient",
    "AirTableField",
    "AirTableError",
    "RecordNotFoundError",
    "ValidationError",
    "BaseManager",
    "TableManager",
]
