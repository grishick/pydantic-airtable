"""
Streamlined configuration management for AirTable connections
"""

import os
from dataclasses import dataclass
from typing import Optional

from .exceptions import ConfigurationError


@dataclass
class AirTableConfig:
    """
    Simplified AirTable configuration
    
    Attributes:
        access_token: AirTable Personal Access Token (required)
        base_id: AirTable base ID (required) 
        table_name: Default table name (optional)
    """
    access_token: str
    base_id: str
    table_name: Optional[str] = None
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.access_token:
            raise ConfigurationError(
                "AirTable Personal Access Token is required. "
                "Get yours from: https://airtable.com/developers/web/api/authentication"
            )
        
        if not self.base_id:
            raise ConfigurationError(
                "AirTable Base ID is required. "
                "Find it in your base URL: https://airtable.com/[BASE_ID]"
            )
        
        # Validate token format (PATs start with 'pat')
        if not self.access_token.startswith('pat'):
            raise ConfigurationError(
                "Invalid access token format. Personal Access Tokens must start with 'pat'. "
                "API keys are no longer supported. "
                "Get a PAT from: https://airtable.com/developers/web/api/authentication"
            )
        
        # Validate base ID format 
        if not self.base_id.startswith('app'):
            raise ConfigurationError(
                "Invalid base ID format. Base IDs must start with 'app'. "
                "Find your base ID in the URL: https://airtable.com/[BASE_ID]"
            )
    
    @classmethod
    def from_env(
        cls,
        access_token: Optional[str] = None,
        base_id: Optional[str] = None,
        table_name: Optional[str] = None,
        env_prefix: str = "AIRTABLE_"
    ) -> 'AirTableConfig':
        """
        Create configuration from environment variables with optional overrides
        
        Args:
            access_token: Override for access token
            base_id: Override for base ID
            table_name: Override for table name
            env_prefix: Environment variable prefix (default: AIRTABLE_)
            
        Returns:
            AirTableConfig instance
            
        Environment Variables:
            AIRTABLE_ACCESS_TOKEN: Personal Access Token
            AIRTABLE_BASE_ID: Base ID
            AIRTABLE_TABLE_NAME: Default table name (optional)
        """
        return cls(
            access_token=access_token or os.getenv(f"{env_prefix}ACCESS_TOKEN", ""),
            base_id=base_id or os.getenv(f"{env_prefix}BASE_ID", ""),
            table_name=table_name or os.getenv(f"{env_prefix}TABLE_NAME")
        )
    
    def with_table(self, table_name: str) -> 'AirTableConfig':
        """
        Create a new config with a different table name
        
        Args:
            table_name: New table name
            
        Returns:
            New AirTableConfig instance
        """
        return AirTableConfig(
            access_token=self.access_token,
            base_id=self.base_id,
            table_name=table_name
        )
    
    def validate_table_name(self, table_name: Optional[str] = None) -> str:
        """
        Validate and return table name
        
        Args:
            table_name: Table name to validate (uses config default if None)
            
        Returns:
            Validated table name
            
        Raises:
            ConfigurationError: If no table name available
        """
        name = table_name or self.table_name
        if not name:
            raise ConfigurationError(
                "Table name is required. Specify it in AirTableConfig or pass as argument."
            )
        return name


# Global configuration instance for convenience
_global_config: Optional[AirTableConfig] = None


def set_global_config(config: AirTableConfig) -> None:
    """
    Set global configuration for convenience
    
    Args:
        config: AirTableConfig instance
    """
    global _global_config
    _global_config = config


def get_global_config() -> AirTableConfig:
    """
    Get global configuration
    
    Returns:
        Global AirTableConfig instance
        
    Raises:
        ConfigurationError: If no global config set
    """
    if _global_config is None:
        raise ConfigurationError(
            "No global configuration set. Call set_global_config() first or "
            "use AirTableConfig.from_env() to create from environment variables."
        )
    return _global_config


def configure_from_env(**overrides) -> AirTableConfig:
    """
    Convenience function to configure from environment and set as global
    
    Args:
        **overrides: Override specific configuration values
        
    Returns:
        AirTableConfig instance (also set as global)
    """
    config = AirTableConfig.from_env(**overrides)
    set_global_config(config)
    return config
