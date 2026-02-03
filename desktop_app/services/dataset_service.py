"""
Dataset service for managing datasets via API
"""

from typing import List, Dict, Any, Optional
from .api_client import APIClient, APIException


class DatasetService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
    
    def get_datasets(self) -> List[Dict[str, Any]]:
        """Get list of all datasets"""
        try:
            response = self.api_client.get('/api/datasets/')
            return response.get('results', [])
        except APIException as e:
            raise DatasetException(f"Failed to fetch datasets: {str(e)}")
    
    def get_dataset(self, dataset_id: int) -> Dict[str, Any]:
        """Get specific dataset details"""
        try:
            return self.api_client.get(f'/api/datasets/{dataset_id}/')
        except APIException as e:
            raise DatasetException(f"Failed to fetch dataset: {str(e)}")
    
    def upload_dataset(self, file_path: str, name: str = None, description: str = None) -> Dict[str, Any]:
        """Upload a new dataset"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {}
                
                if name:
                    data['name'] = name
                if description:
                    data['description'] = description
                
                return self.api_client.post('/api/datasets/upload/', data=data, files=files)
        except FileNotFoundError:
            raise DatasetException("File not found")
        except APIException as e:
            raise DatasetException(f"Failed to upload dataset: {str(e)}")
    
    def delete_dataset(self, dataset_id: int) -> bool:
        """Delete a dataset"""
        try:
            self.api_client.delete(f'/api/datasets/{dataset_id}/delete_dataset/')
            return True
        except APIException as e:
            raise DatasetException(f"Failed to delete dataset: {str(e)}")
    
    def get_dataset_statistics(self, dataset_id: int) -> Dict[str, Any]:
        """Get dataset statistics"""
        try:
            return self.api_client.get(f'/api/datasets/{dataset_id}/statistics/')
        except APIException as e:
            raise DatasetException(f"Failed to fetch statistics: {str(e)}")
    
    def get_dataset_columns(self, dataset_id: int) -> List[Dict[str, Any]]:
        """Get dataset column information"""
        try:
            return self.api_client.get(f'/api/datasets/{dataset_id}/columns/')
        except APIException as e:
            raise DatasetException(f"Failed to fetch columns: {str(e)}")
    
    def get_dataset_history(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get dataset history with pagination"""
        try:
            params = {'page': page, 'page_size': page_size}
            return self.api_client.get('/api/history/datasets/', params=params)
        except APIException as e:
            raise DatasetException(f"Failed to fetch history: {str(e)}")
    
    def get_history_status(self) -> Dict[str, Any]:
        """Get history status information"""
        try:
            return self.api_client.get('/api/history/status/')
        except APIException as e:
            raise DatasetException(f"Failed to fetch history status: {str(e)}")
    
    def download_pdf_report(self, dataset_id: int) -> bytes:
        """Download PDF report for a dataset"""
        try:
            # Use the raw request method to get binary data
            response = self.api_client.get_raw(f'/api/reports/pdf/{dataset_id}/')
            return response.content
        except APIException as e:
            raise DatasetException(f"Failed to download PDF report: {str(e)}")


class DatasetException(Exception):
    """Custom exception for dataset operations"""
    pass