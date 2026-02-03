"""
API root views for providing API documentation and navigation
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.urls import reverse
from django.http import JsonResponse


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root endpoint providing navigation to all available endpoints
    """
    base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
    
    api_endpoints = {
        'message': 'Welcome to the Dataset Analysis API',
        'version': '1.0.0',
        'documentation': {
            'equipment_api_guide': 'See EQUIPMENT_API_GUIDE.md for detailed documentation',
            'testing_guide': 'See TESTING_GUIDE.md for testing instructions'
        },
        'endpoints': {
            'datasets': {
                'list_datasets': f'{base_url}/api/datasets/',
                'upload_dataset': f'{base_url}/api/datasets/upload/',
                'dataset_detail': f'{base_url}/api/datasets/{{id}}/',
                'dataset_statistics': f'{base_url}/api/datasets/{{id}}/statistics/',
                'dataset_columns': f'{base_url}/api/datasets/{{id}}/columns/',
            },
            'equipment_specific': {
                'upload_equipment_csv': f'{base_url}/api/equipment/upload/',
                'validate_csv': f'{base_url}/api/equipment/validate/',
                'data_summary_all': f'{base_url}/api/equipment/summary/',
                'data_summary_specific': f'{base_url}/api/equipment/summary/{{dataset_id}}/',
                'equipment_preview': f'{base_url}/api/equipment/preview/{{dataset_id}}/',
            },
            'statistics': {
                'list_statistics': f'{base_url}/api/statistics/',
                'statistics_detail': f'{base_url}/api/statistics/{{id}}/',
                'numeric_summary': f'{base_url}/api/statistics/{{id}}/numeric_summary/',
                'categorical_summary': f'{base_url}/api/statistics/{{id}}/categorical_summary/',
            },
            'columns': {
                'list_columns': f'{base_url}/api/columns/',
                'columns_by_dataset': f'{base_url}/api/columns/?dataset={{dataset_id}}',
            },
            'admin': {
                'admin_interface': f'{base_url}/admin/',
            }
        },
        'quick_start': {
            'step_1': 'Upload equipment CSV: POST /api/equipment/upload/',
            'step_2': 'Get data summary: GET /api/equipment/summary/',
            'step_3': 'View in admin: /admin/',
            'required_csv_columns': [
                'equipment_id (or id, equipment_number)',
                'equipment_type (or type, category)',
                'flowrate (or flow_rate, flow, rate)',
                'pressure (or press, psi, bar)',
                'temperature (or temp, celsius, fahrenheit)'
            ]
        },
        'sample_requests': {
            'upload_csv': {
                'method': 'POST',
                'url': '/api/equipment/upload/',
                'content_type': 'multipart/form-data',
                'body': 'file=@equipment_data.csv&name=My Equipment Dataset'
            },
            'get_summary': {
                'method': 'GET',
                'url': '/api/equipment/summary/',
                'description': 'Get combined summary of all datasets'
            },
            'validate_csv': {
                'method': 'POST',
                'url': '/api/equipment/validate/',
                'content_type': 'multipart/form-data',
                'body': 'file=@equipment_data.csv'
            }
        }
    }
    
    return Response(api_endpoints)


def home_redirect(request):
    """
    Simple redirect from root to API root
    """
    return JsonResponse({
        'message': 'Dataset Analysis API',
        'api_root': '/api/',
        'admin': '/admin/',
        'equipment_endpoints': {
            'upload': '/api/equipment/upload/',
            'summary': '/api/equipment/summary/',
            'validate': '/api/equipment/validate/'
        },
        'note': 'Visit /api/ for complete API documentation'
    })