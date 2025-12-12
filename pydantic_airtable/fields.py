"""
AirTable field definitions and type mappings
"""

from typing import Any, Optional, Type
from datetime import datetime, date, timedelta
from pydantic import Field
from enum import Enum


class AirTableFieldType(str, Enum):
    """AirTable field types"""
    # Text fields
    SINGLE_LINE_TEXT = "singleLineText"
    LONG_TEXT = "multilineText"
    EMAIL = "email"
    URL = "url"
    PHONE = "phoneNumber"
    
    # Numeric fields
    NUMBER = "number"
    CURRENCY = "currency"
    PERCENT = "percent"
    RATING = "rating"
    DURATION = "duration"
    
    # Date/Time fields
    DATE = "date"
    DATETIME = "dateTime"
    
    # Selection fields
    CHECKBOX = "checkbox"
    SELECT = "singleSelect"
    MULTI_SELECT = "multipleSelects"
    
    # Relational fields
    LINKED_RECORD = "multipleRecordLinks"
    LOOKUP = "lookup"
    ROLLUP = "rollup"
    COUNT = "count"
    
    # Special fields
    ATTACHMENT = "multipleAttachments"
    BARCODE = "barcode"
    BUTTON = "button"
    USER = "multipleCollaborators"
    
    # Computed/System fields
    FORMULA = "formula"
    AUTO_NUMBER = "autoNumber"
    CREATED_TIME = "createdTime"
    MODIFIED_TIME = "lastModifiedTime"
    CREATED_BY = "createdBy"
    MODIFIED_BY = "lastModifiedBy"


def AirTableField(
    airtable_field_name: Optional[str] = None,
    airtable_field_type: Optional[AirTableFieldType] = None,
    read_only: bool = False,
    **kwargs
) -> Any:
    """
    Create a Pydantic field with AirTable-specific metadata.

    Args:
        airtable_field_name: The name of the field in AirTable (if different from Python field name)
        airtable_field_type: The AirTable field type
        read_only: Whether this field should be excluded from create/update operations
        **kwargs: Additional Pydantic Field arguments
    """
    json_schema_extra = kwargs.get("json_schema_extra", {})
    json_schema_extra.update({
        "airtable_field_name": airtable_field_name,
        "airtable_field_type": airtable_field_type,
        "airtable_read_only": read_only,
    })
    kwargs["json_schema_extra"] = json_schema_extra

    return Field(**kwargs)


class TypeMapper:
    """Maps Python types to AirTable field types"""

    TYPE_MAPPING = {
        str: AirTableFieldType.SINGLE_LINE_TEXT,
        int: AirTableFieldType.NUMBER,
        float: AirTableFieldType.NUMBER,
        bool: AirTableFieldType.CHECKBOX,
        datetime: AirTableFieldType.DATETIME,
        date: AirTableFieldType.DATE,
        timedelta: AirTableFieldType.DURATION,
    }

    @classmethod
    def get_airtable_type(cls, python_type: Type) -> AirTableFieldType:
        """Get the corresponding AirTable field type for a Python type"""
        return cls.TYPE_MAPPING.get(python_type, AirTableFieldType.SINGLE_LINE_TEXT)

    @classmethod
    def format_value_for_airtable(cls, value: Any, field_type: AirTableFieldType) -> Any:
        """Format a Python value for AirTable API"""
        if value is None:
            return None

        if field_type == AirTableFieldType.DATETIME:
            if isinstance(value, datetime):
                return value.isoformat()
        elif field_type == AirTableFieldType.DATE:
            if isinstance(value, (datetime, date)):
                return value.strftime("%Y-%m-%d")
        elif field_type == AirTableFieldType.DURATION:
            # AirTable stores duration as total seconds (integer)
            if isinstance(value, timedelta):
                return int(value.total_seconds())
            elif isinstance(value, (int, float)):
                return int(value)
        elif field_type == AirTableFieldType.CHECKBOX:
            return bool(value)
        elif field_type in [AirTableFieldType.NUMBER, AirTableFieldType.CURRENCY, AirTableFieldType.PERCENT]:
            return float(value) if not isinstance(value, bool) else value

        return value

    @classmethod
    def parse_value_from_airtable(cls, value: Any, field_type: AirTableFieldType) -> Any:
        """Parse a value from AirTable API response"""
        if value is None:
            return None

        if field_type == AirTableFieldType.DATETIME:
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    return value
        elif field_type == AirTableFieldType.DATE:
            if isinstance(value, str):
                try:
                    return datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    return value
        elif field_type == AirTableFieldType.DURATION:
            # AirTable returns duration as total seconds (integer)
            if isinstance(value, (int, float)):
                return timedelta(seconds=value)
        elif field_type == AirTableFieldType.CHECKBOX:
            return bool(value)

        return value
