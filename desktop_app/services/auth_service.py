"""
Authentication service for handling login/logout
"""

import json
import os
from typing import Optional, Dict, Any
from .api_client import APIClient, APIException


class AuthService:
    def __init__(self):
        self.api_client = APIClient()
        self.token_file = os.path.expanduser("~/.chemical_equipment_visualizer_token")
        self.current_user = None
        self._load_token()
    
    def _load_token(self):
        """Load saved authentication token"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    token = data.get('access_token')
                    if token:
                        self.api_client.set_auth_token(token)
                        # Verify token is still valid
                        try:
                            user_data = self.api_client.get('/api/auth/status/')
                            if user_data.get('authenticated'):
                                self.current_user = user_data.get('user')
                                return
                        except APIException:
                            pass
                        
                # Token invalid, clear it
                self._clear_token()
        except Exception:
            self._clear_token()
    
    def _save_token(self, access_token: str, refresh_token: str):
        """Save authentication tokens"""
        try:
            with open(self.token_file, 'w') as f:
                json.dump({
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, f)
        except Exception as e:
            print(f"Failed to save token: {e}")
    
    def _clear_token(self):
        """Clear saved authentication token"""
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
        except Exception:
            pass
        
        self.api_client.clear_auth_token()
        self.current_user = None
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user and save token"""
        try:
            response = self.api_client.post('/api/auth/login/', {
                'username': username,
                'password': password
            })
            
            user = response.get('user')
            tokens = response.get('tokens')
            
            if user and tokens:
                self.current_user = user
                access_token = tokens.get('access')
                refresh_token = tokens.get('refresh')
                
                if access_token:
                    self.api_client.set_auth_token(access_token)
                    self._save_token(access_token, refresh_token)
                
                return {'success': True, 'user': user}
            else:
                return {'success': False, 'error': 'Invalid response from server'}
                
        except APIException as e:
            return {'success': False, 'error': str(e)}
    
    def register(self, username: str, password: str, email: str) -> Dict[str, Any]:
        """Register new user"""
        try:
            response = self.api_client.post('/api/auth/register/', {
                'username': username,
                'password': password,
                'email': email
            })
            
            user = response.get('user')
            tokens = response.get('tokens')
            
            if user and tokens:
                self.current_user = user
                access_token = tokens.get('access')
                refresh_token = tokens.get('refresh')
                
                if access_token:
                    self.api_client.set_auth_token(access_token)
                    self._save_token(access_token, refresh_token)
                
                return {'success': True, 'user': user}
            else:
                return {'success': False, 'error': 'Invalid response from server'}
                
        except APIException as e:
            return {'success': False, 'error': str(e)}
    
    def logout(self):
        """Logout user and clear token"""
        try:
            # Try to logout on server
            self.api_client.post('/api/auth/logout/', {})
        except APIException:
            pass  # Ignore logout errors
        
        self._clear_token()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current user info"""
        return self.current_user
    
    def get_api_client(self) -> APIClient:
        """Get authenticated API client"""
        return self.api_client