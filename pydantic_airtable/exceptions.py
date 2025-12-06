"""
Custom exceptions for the Pydantic AirTable library
"""


class AirTableError(Exception):
    """Base exception for all AirTable related errors"""
    pass


class RecordNotFoundError(AirTableError):
    """Raised when a requested record is not found in AirTable"""
    pass


class ValidationError(AirTableError):
    """Raised when data validation fails"""
    pass


class APIError(AirTableError):
    """Raised when AirTable API returns an error"""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class ConfigurationError(AirTableError):
    """Raised when there's an issue with configuration"""
    pass

