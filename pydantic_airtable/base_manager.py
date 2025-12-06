"""
AirTable Base Management - Create, list, and manage AirTable bases
"""

import json
import requests
from typing import Any, Dict, List, Optional
from .exceptions import APIError
from .client import AirTableClient


class BaseManager:
    """
    Manager for AirTable base operations using the AirTable API
    """
    
    BASE_URL = "https://api.airtable.com/v0"
    META_API_URL = "https://api.airtable.com/v0/meta"
    
    def __init__(self, access_token: str):
        """
        Initialize Base Manager
        
        Args:
            access_token: AirTable Personal Access Token with base management permissions
        """
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        })
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions"""
        try:
            data = response.json()
        except:
            data = {"error": {"message": response.text}}
        
        if not response.ok:
            error_message = data.get("error", {}).get("message", f"HTTP {response.status_code}")
            
            # Enhanced error reporting for debugging
            print(f"🔍 API Error Debug Info:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            print(f"   Response Text: {response.text}")
            print(f"   Parsed Data: {data}")
            
            raise APIError(
                message=f"{error_message} (Status: {response.status_code})",
                status_code=response.status_code,
                response_data=data
            )
        
        return data
    
    def list_bases(self) -> List[Dict[str, Any]]:
        """
        List all bases accessible with the current access token
        
        Returns:
            List of base information dictionaries
        """
        response = self.session.get(f"{self.META_API_URL}/bases")
        data = self._handle_response(response)
        return data.get("bases", [])
    
    def get_base_schema(self, base_id: str) -> Dict[str, Any]:
        """
        Get the schema of a specific base
        
        Args:
            base_id: AirTable base ID
            
        Returns:
            Base schema information including tables and fields
        """
        response = self.session.get(f"{self.META_API_URL}/bases/{base_id}/tables")
        return self._handle_response(response)
    
    def create_base(
        self, 
        name: str, 
        tables: List[Dict[str, Any]], 
        workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new AirTable base
        
        Args:
            name: Name of the new base
            tables: List of table configurations
            workspace_id: Optional workspace ID to create base in
            
        Returns:
            Created base information
        """
        payload = {
            "name": name,
            "tables": tables
        }
        
        if workspace_id:
            payload["workspaceId"] = workspace_id
        
        # Debug: Print the payload being sent
        print(f"🔍 Debug: Creating base with payload:")
        print(f"   Name: {name}")
        print(f"   Tables: {len(tables)} table(s)")
        print(f"   Workspace ID: {workspace_id or 'None'}")
        print(f"   Full payload: {json.dumps(payload, indent=2)}")
        
        response = self.session.post(f"{self.META_API_URL}/bases", json=payload)
        return self._handle_response(response)
    
    def delete_base(self, base_id: str) -> Dict[str, Any]:
        """
        Delete an AirTable base
        
        Args:
            base_id: AirTable base ID to delete
            
        Returns:
            Deletion confirmation
        """
        response = self.session.delete(f"{self.META_API_URL}/bases/{base_id}")
        return self._handle_response(response)
    
    def get_base_info(self, base_id: str) -> Dict[str, Any]:
        """
        Get information about a specific base
        
        Args:
            base_id: AirTable base ID
            
        Returns:
            Base information
        """
        bases = self.list_bases()
        for base in bases:
            if base.get("id") == base_id:
                return base
        raise APIError(f"Base {base_id} not found", status_code=404)
    
    def create_table_manager(self, base_id: str) -> 'TableManager':
        """
        Create a TableManager for a specific base
        
        Args:
            base_id: AirTable base ID
            
        Returns:
            TableManager instance for the base
        """
        from .table_manager import TableManager
        return TableManager(self.access_token, base_id)

