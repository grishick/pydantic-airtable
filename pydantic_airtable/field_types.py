"""
Streamlined field type system with smart detection and minimal boilerplate
"""

import re
from typing import Any, Dict, Optional, Type, Union, get_origin, get_args
from datetime import datetime, date
from enum import Enum
from pydantic import Field
from pydantic.fields import FieldInfo

from .fields import AirTableFieldType


class FieldTypeResolver:
    """
    Unified field type detection and conversion
    Eliminates duplication and provides smart defaults
    """
    
    # Core type mappings
    PYTHON_TO_AIRTABLE = {
        str: AirTableFieldType.SINGLE_LINE_TEXT,
        int: AirTableFieldType.NUMBER,
        float: AirTableFieldType.NUMBER,
        bool: AirTableFieldType.CHECKBOX,
        datetime: AirTableFieldType.DATETIME,
        date: AirTableFieldType.DATE,
        list: AirTableFieldType.MULTI_SELECT,
    }
    
    # Field name patterns for smart detection
    EMAIL_PATTERNS = [
        r'email', r'e_mail', r'mail', r'contact'
    ]
    
    URL_PATTERNS = [
        r'url', r'link', r'website', r'site', r'href'
    ]
    
    PHONE_PATTERNS = [
        r'phone', r'tel', r'mobile', r'cell'
    ]
    
    LONG_TEXT_PATTERNS = [
        r'description', r'comment', r'note', r'bio', r'summary', 
        r'content', r'body', r'message', r'detail'
    ]
    
    CURRENCY_PATTERNS = [
        r'price', r'cost', r'amount', r'fee', r'salary', r'wage',
        r'revenue', r'budget', r'payment'
    ]
    
    PERCENT_PATTERNS = [
        r'percent', r'percentage', r'rate', r'ratio'
    ]
    
    @classmethod
    def resolve_field_type(
        cls,
        field_name: str,
        python_type: Type,
        field_info: Optional[FieldInfo] = None,
        explicit_type: Optional[AirTableFieldType] = None
    ) -> AirTableFieldType:
        """
        Resolve AirTable field type from multiple sources
        
        Priority:
        1. Explicit type specification
        2. Field info metadata
        3. Smart detection from field name
        4. Python type mapping
        5. Default fallback
        
        Args:
            field_name: Python field name
            python_type: Python type annotation
            field_info: Pydantic field info
            explicit_type: Explicitly specified AirTable type
            
        Returns:
            Resolved AirTable field type
        """
        # 1. Explicit type takes precedence
        if explicit_type:
            return explicit_type
        
        # 2. Check field info for existing type specification
        if field_info and hasattr(field_info, 'json_schema_extra'):
            extra = field_info.json_schema_extra or {}
            if isinstance(extra, dict) and 'airtable_field_type' in extra:
                return extra['airtable_field_type']
        
        # 3. Smart detection from field name (for string types)
        if cls._is_string_type(python_type):
            smart_type = cls._detect_from_field_name(field_name)
            if smart_type:
                return smart_type
        
        # 4. Python type mapping
        base_type = cls._extract_base_type(python_type)
        if base_type in cls.PYTHON_TO_AIRTABLE:
            airtable_type = cls.PYTHON_TO_AIRTABLE[base_type]
            
            # Further refinement for numbers
            if airtable_type == AirTableFieldType.NUMBER:
                return cls._refine_number_type(field_name)
            
            return airtable_type
        
        # 5. Handle enums
        if cls._is_enum_type(python_type):
            return AirTableFieldType.SELECT
        
        # 6. Default fallback
        return AirTableFieldType.SINGLE_LINE_TEXT
    
    @classmethod
    def _is_string_type(cls, python_type: Type) -> bool:
        """Check if type is string-based"""
        base_type = cls._extract_base_type(python_type)
        return base_type == str
    
    @classmethod
    def _is_enum_type(cls, python_type: Type) -> bool:
        """Check if type is enum-based"""
        base_type = cls._extract_base_type(python_type)
        return (isinstance(base_type, type) and 
                issubclass(base_type, Enum))
    
    @classmethod
    def _extract_base_type(cls, python_type: Type) -> Type:
        """
        Extract base type from complex type annotations
        
        Handles:
        - Optional[T] -> T
        - Union[T, None] -> T  
        - List[T] -> list
        - etc.
        """
        # Handle Optional and Union types
        origin = get_origin(python_type)
        if origin is Union:
            args = get_args(python_type)
            non_none_args = [arg for arg in args if arg != type(None)]
            if non_none_args:
                return cls._extract_base_type(non_none_args[0])
        
        # Handle generic types (List, Dict, etc.)
        if origin:
            return origin
        
        return python_type
    
    @classmethod
    def _detect_from_field_name(cls, field_name: str) -> Optional[AirTableFieldType]:
        """
        Smart field type detection based on field name patterns
        
        Args:
            field_name: Field name to analyze
            
        Returns:
            Detected field type or None
        """
        name_lower = field_name.lower()
        
        # Email detection
        if any(re.search(pattern, name_lower) for pattern in cls.EMAIL_PATTERNS):
            return AirTableFieldType.EMAIL
        
        # URL detection  
        if any(re.search(pattern, name_lower) for pattern in cls.URL_PATTERNS):
            return AirTableFieldType.URL
        
        # Phone detection
        if any(re.search(pattern, name_lower) for pattern in cls.PHONE_PATTERNS):
            return AirTableFieldType.PHONE
        
        # Long text detection
        if any(re.search(pattern, name_lower) for pattern in cls.LONG_TEXT_PATTERNS):
            return AirTableFieldType.LONG_TEXT
        
        return None
    
    @classmethod
    def _refine_number_type(cls, field_name: str) -> AirTableFieldType:
        """
        Refine number type based on field name
        
        Args:
            field_name: Field name to analyze
            
        Returns:
            Refined number field type
        """
        name_lower = field_name.lower()
        
        # Currency detection
        if any(re.search(pattern, name_lower) for pattern in cls.CURRENCY_PATTERNS):
            return AirTableFieldType.CURRENCY
        
        # Percentage detection
        if any(re.search(pattern, name_lower) for pattern in cls.PERCENT_PATTERNS):
            return AirTableFieldType.PERCENT
        
        return AirTableFieldType.NUMBER
    
    @classmethod
    def get_field_options(cls, field_type: AirTableFieldType, **kwargs) -> Dict[str, Any]:
        """
        Generate field options for specific AirTable field types
        
        Args:
            field_type: AirTable field type
            **kwargs: Additional options
            
        Returns:
            Field options dictionary
        """
        options = {}
        
        if field_type == AirTableFieldType.CHECKBOX:
            options.update({
                "icon": kwargs.get("icon", "check"),
                "color": kwargs.get("color", "greenBright")
            })
        
        elif field_type == AirTableFieldType.SELECT:
            choices = kwargs.get("choices", [])
            if choices:
                options["choices"] = [{"name": choice} for choice in choices]
        
        elif field_type == AirTableFieldType.MULTI_SELECT:
            choices = kwargs.get("choices", [])
            if choices:
                options["choices"] = [{"name": choice} for choice in choices]
        
        elif field_type == AirTableFieldType.CURRENCY:
            options.update({
                "precision": kwargs.get("precision", 2),
                "symbol": kwargs.get("symbol", "$")
            })
        
        elif field_type == AirTableFieldType.PERCENT:
            options.update({
                "precision": kwargs.get("precision", 1)
            })
        
        return options


def airtable_field(
    *,
    field_type: Optional[AirTableFieldType] = None,
    field_name: Optional[str] = None,
    read_only: bool = False,
    choices: Optional[list] = None,
    **field_kwargs
) -> Any:
    """
    Streamlined AirTable field with smart defaults
    
    Args:
        field_type: Explicit AirTable field type (auto-detected if None)
        field_name: AirTable field name (uses Python name if None) 
        read_only: Whether field is read-only
        choices: For select/multi-select fields
        **field_kwargs: Additional Pydantic Field() arguments
        
    Returns:
        Pydantic Field with AirTable metadata
    """
    # Build AirTable metadata
    airtable_metadata = {}
    
    if field_type:
        airtable_metadata['airtable_field_type'] = field_type
    
    if field_name:
        airtable_metadata['airtable_field_name'] = field_name
    
    if read_only:
        airtable_metadata['airtable_read_only'] = True
    
    if choices:
        airtable_metadata['airtable_choices'] = choices
    
    # Merge with existing json_schema_extra
    existing_extra = field_kwargs.get('json_schema_extra', {})
    if callable(existing_extra):
        # If it's a function, we can't easily merge, so replace
        field_kwargs['json_schema_extra'] = airtable_metadata
    else:
        # Merge dictionaries
        merged_extra = {**(existing_extra or {}), **airtable_metadata}
        field_kwargs['json_schema_extra'] = merged_extra
    
    return Field(**field_kwargs)
