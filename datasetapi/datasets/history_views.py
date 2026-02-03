"""
History management views for dataset cleanup and management
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.conf import settings
import logging

from .history_utils import (
    cleanup_all_old_datasets, get_dataset_history_info,
    trigger_cleanup_if_needed, get_datasets_for_cleanup_preview
)
from .models import Dataset

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def history_status(request):
    """
    Get current history status and information
    
    GET /api/history/status/
    
    Returns:
        JSON with history information
    """
    try:
        history_info = get_dataset_history_info()
        
        # Add cleanup preview
        cleanup_preview = get_datasets_for_cleanup_preview()
        
        response_data = {
            'history_info': history_info,
            'cleanup_preview': {
                'datasets_to_be_deleted': len(cleanup_preview),
                'datasets': cleanup_preview
            },
            'settings': {
                'max_datasets_allowed': getattr(settings, 'MAX_DATASETS_PER_USER', 5)
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting history status: {str(e)}")
        return Response({
            'error': 'Failed to get history status',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])  # Only admin users can trigger manual cleanup
def manual_cleanup(request):
    """
    Manually trigger cleanup of old datasets
    
    POST /api/history/cleanup/
    
    Returns:
        JSON with cleanup results
    """
    try:
        # Get preview before cleanup
        preview = get_datasets_for_cleanup_preview()
        
        if not preview:
            return Response({
                'message': 'No cleanup needed',
                'datasets_deleted': 0,
                'current_count': Dataset.objects.count()
            }, status=status.HTTP_200_OK)
        
        # Perform cleanup
        cleanup_result = cleanup_all_old_datasets()
        
        return Response({
            'message': 'Manual cleanup completed',
            'cleanup_result': cleanup_result,
            'datasets_previewed': len(preview)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in manual cleanup: {str(e)}")
        return Response({
            'error': 'Manual cleanup failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cleanup_preview(request):
    """
    Preview which datasets would be deleted in the next cleanup
    
    GET /api/history/cleanup-preview/
    
    Returns:
        JSON with datasets that would be deleted
    """
    try:
        preview = get_datasets_for_cleanup_preview()
        
        return Response({
            'datasets_to_be_deleted': len(preview),
            'datasets': preview,
            'max_datasets_allowed': getattr(settings, 'MAX_DATASETS_PER_USER', 5),
            'current_total': Dataset.objects.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting cleanup preview: {str(e)}")
        return Response({
            'error': 'Failed to get cleanup preview',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dataset_history(request):
    """
    Get paginated list of datasets ordered by upload date
    
    GET /api/history/datasets/
    
    Query parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 10, max: 50)
    
    Returns:
        Paginated list of datasets
    """
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 10)), 50)  # Max 50 items per page
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get datasets ordered by upload date (newest first)
        total_count = Dataset.objects.count()
        datasets = Dataset.objects.select_related('summary').order_by('-upload_date')[offset:offset + page_size]
        
        # Prepare dataset list
        dataset_list = []
        for dataset in datasets:
            dataset_info = {
                'id': dataset.id,
                'name': dataset.name,
                'description': dataset.description,
                'file_name': dataset.file_name,
                'file_type': dataset.file_type,
                'upload_date': dataset.upload_date,
                'total_rows': dataset.total_rows,
                'total_columns': dataset.total_columns,
                'is_processed': dataset.is_processed,
                'file_size': dataset.file_size
            }
            
            # Add summary info if available
            if hasattr(dataset, 'summary') and dataset.summary:
                dataset_info['summary'] = {
                    'total_records': dataset.summary.total_records,
                    'avg_flowrate': dataset.summary.avg_flowrate,
                    'avg_pressure': dataset.summary.avg_pressure,
                    'avg_temperature': dataset.summary.avg_temperature,
                    'equipment_types': len(dataset.summary.equipment_type_distribution) if dataset.summary.equipment_type_distribution else 0
                }
            
            dataset_list.append(dataset_info)
        
        # Calculate pagination info
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1
        
        return Response({
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_previous': has_previous,
                'next_page': page + 1 if has_next else None,
                'previous_page': page - 1 if has_previous else None
            },
            'datasets': dataset_list
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'error': 'Invalid pagination parameters',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error getting dataset history: {str(e)}")
        return Response({
            'error': 'Failed to get dataset history',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_specific_dataset(request, dataset_id):
    """
    Delete a specific dataset (with confirmation)
    
    DELETE /api/history/datasets/{dataset_id}/
    
    Body (optional):
    {
        "confirm": true
    }
    
    Returns:
        JSON with deletion result
    """
    try:
        # Check for confirmation
        confirm = request.data.get('confirm', False)
        if not confirm:
            return Response({
                'error': 'Deletion requires confirmation',
                'message': 'Send {"confirm": true} in request body to confirm deletion',
                'dataset_id': dataset_id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the dataset
        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except Dataset.DoesNotExist:
            return Response({
                'error': 'Dataset not found',
                'dataset_id': dataset_id
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Store dataset info before deletion
        dataset_info = {
            'id': dataset.id,
            'name': dataset.name,
            'file_name': dataset.file_name,
            'upload_date': dataset.upload_date
        }
        
        # Delete the dataset (cascade will handle related objects)
        dataset.delete()
        
        logger.info(f"Dataset {dataset_id} deleted by user {request.user.username}")
        
        return Response({
            'message': 'Dataset deleted successfully',
            'deleted_dataset': dataset_info
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error deleting dataset {dataset_id}: {str(e)}")
        return Response({
            'error': 'Failed to delete dataset',
            'details': str(e),
            'dataset_id': dataset_id
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def history_settings(request):
    """
    Get current history management settings
    
    GET /api/history/settings/
    
    Returns:
        JSON with current settings
    """
    try:
        settings_info = {
            'max_datasets_per_user': getattr(settings, 'MAX_DATASETS_PER_USER', 5),
            'current_dataset_count': Dataset.objects.count(),
            'processed_dataset_count': Dataset.objects.filter(is_processed=True).count(),
            'auto_cleanup_enabled': True,  # Always enabled in this implementation
            'cleanup_trigger': 'on_upload',  # Cleanup is triggered when new datasets are uploaded
        }
        
        return Response(settings_info, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting history settings: {str(e)}")
        return Response({
            'error': 'Failed to get history settings',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)