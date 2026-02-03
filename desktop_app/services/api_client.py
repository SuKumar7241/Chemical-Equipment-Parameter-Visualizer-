"""
API Client for communicating with Django REST API
"""

import requests
import json
from typing import Optional, Dict, Any


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
        
    def set_auth_token(self, token: str):
        """Set authentication token for requests"""
        self.session.headers.update({'Authorization': f'Bearer {token}'})
        
    def clear_auth_token(self):
        """Clear authentication token"""
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            raise APIException(f"Request failed: {str(e)}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        response = self._make_request('GET', endpoint, params=params)
        return self._handle_response(response)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request"""
        kwargs = {}
        if files:
            kwargs['files'] = files
            if data:
                kwargs['data'] = data
        else:
            kwargs['json'] = data
            
        response = self._make_request('POST', endpoint, **kwargs)
        return self._handle_response(response)
    
    def delete(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make DELETE request"""
        kwargs = {}
        if data:
            kwargs['json'] = data
            
        response = self._make_request('DELETE', endpoint, **kwargs)
        return self._handle_response(response)
    
    def get_raw(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Make GET request and return raw response (for binary data like PDFs)"""
        response = self._make_request('GET', endpoint, params=params)
        
        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', f'HTTP {response.status_code}')
            except json.JSONDecodeError:
                error_msg = f'HTTP {response.status_code}: {response.text}'
            raise APIException(error_msg)
        
        return response
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response"""
        try:
            if response.status_code == 204:  # No content
                return {}
                
            data = response.json()
            
            if response.status_code >= 400:
                error_msg = data.get('error', f'HTTP {response.status_code}')
                raise APIException(error_msg)
                
            return data
            
        except json.JSONDecodeError:
            if response.status_code >= 400:
                raise APIException(f"HTTP {response.status_code}: {response.text}")
            return {}


class APIException(Exception):
    """Custom exception for API errors"""
    pass