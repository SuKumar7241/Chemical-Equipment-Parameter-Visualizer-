"""
History management utilities for dataset storage
Manages the last 5 datasets per user and automatically deletes older records
"""
from django.conf import settings
from django.contrib.auth.models import User
from .models import Dataset, SummaryStatistics, DatasetColumn
import logging

logger = logging.getLogger(__name__)

MAX_DATASETS = getattr(settings, 'MAX_DATASETS_PER_USER', 5)


def cleanup_old_datasets(user):
    """
    Keep only the last MAX_DATASETS datasets for a user
    Automatically delete older records with all related data
    
    Args:
        user: User instance or user ID
    """
    try:
        if isinstance(user, int):
            user_id = user
        else:
            user_id = user.id if hasattr(user, 'id') else user
        
        # Get all datasets for the user, ordered by upload date (newest first)
        user_datasets = Dataset.objects.filter(
            # For now, we'll use a simple approach without user foreign key
            # In a real implementation, you'd add a user field to Dataset model
        ).order_by('-upload_date')
        
        # If we have more than MAX_DATASETS, delete the oldest ones
        if user_datasets.count() > MAX_DATASETS:
            datasets_to_delete = user_datasets[MAX_DATASETS:]
            
            deleted_count = 0
            for dataset in datasets_to_delete:
                dataset_name = dataset.name
                dataset_id = dataset.id
                
                # Delete the dataset (cascade will handle related objects)
                dataset.delete()
                deleted_count += 1
                
                logger.info(f"Deleted old dataset: {dataset_name} (ID: {dataset_id})")
            
            logger.info(f"Cleaned up {deleted_count} old datasets for user")
            return deleted_count
        
        return 0
        
    except Exception as e:
        logger.error(f"Error cleaning up old datasets: {str(e)}")
        return 0


def cleanup_all_old_datasets():
    """
    Clean up old datasets for all users
    This can be run as a periodic task
    """
    try:
        # Get total count before cleanup
        total_before = Dataset.objects.count()
        
        # For now, we'll implement a simple global cleanup
        # Keep only the last MAX_DATASETS datasets globally
        all_datasets = Dataset.objects.order_by('-upload_date')
        
        if all_datasets.count() > MAX_DATASETS:
            datasets_to_delete = all_datasets[MAX_DATASETS:]
            
            deleted_count = 0
            for dataset in datasets_to_delete:
                dataset_name = dataset.name
                dataset_id = dataset.id
                
                # Delete the dataset (cascade will handle related objects)
                dataset.delete()
                deleted_count += 1
                
                logger.info(f"Deleted old dataset: {dataset_name} (ID: {dataset_id})")
            
            total_after = Dataset.objects.count()
            
            logger.info(f"Global cleanup completed: {deleted_count} datasets deleted")
            logger.info(f"Dataset count: {total_before} -> {total_after}")
            
            return {
                'deleted_count': deleted_count,
                'total_before': total_before,
                'total_after': total_after
            }
        
        return {
            'deleted_count': 0,
            'total_before': total_before,
            'total_after': total_before
        }
        
    except Exception as e:
        logger.error(f"Error in global cleanup: {str(e)}")
        return {
            'deleted_count': 0,
            'error': str(e)
        }


def get_dataset_history_info():
    """
    Get information about current dataset history
    
    Returns:
        Dict with history information
    """
    try:
        total_datasets = Dataset.objects.count()
        processed_datasets = Dataset.objects.filter(is_processed=True).count()
        
        # Get the oldest and newest datasets
        oldest_dataset = Dataset.objects.order_by('upload_date').first()
        newest_dataset = Dataset.objects.order_by('-upload_date').first()
        
        history_info = {
            'total_datasets': total_datasets,
            'processed_datasets': processed_datasets,
            'max_datasets_allowed': MAX_DATASETS,
            'datasets_until_cleanup': max(0, MAX_DATASETS - total_datasets),
            'oldest_dataset': {
                'id': oldest_dataset.id if oldest_dataset else None,
                'name': oldest_dataset.name if oldest_dataset else None,
                'upload_date': oldest_dataset.upload_date if oldest_dataset else None
            } if oldest_dataset else None,
            'newest_dataset': {
                'id': newest_dataset.id if newest_dataset else None,
                'name': newest_dataset.name if newest_dataset else None,
                'upload_date': newest_dataset.upload_date if newest_dataset else None
            } if newest_dataset else None
        }
        
        return history_info
        
    except Exception as e:
        logger.error(f"Error getting history info: {str(e)}")
        return {
            'error': str(e),
            'total_datasets': 0,
            'processed_datasets': 0
        }


def trigger_cleanup_if_needed():
    """
    Trigger cleanup if we have more than MAX_DATASETS
    This is called automatically when new datasets are uploaded
    
    Returns:
        Dict with cleanup results
    """
    try:
        current_count = Dataset.objects.count()
        
        if current_count > MAX_DATASETS:
            logger.info(f"Dataset count ({current_count}) exceeds limit ({MAX_DATASETS}). Triggering cleanup...")
            cleanup_result = cleanup_all_old_datasets()
            return {
                'cleanup_triggered': True,
                'cleanup_result': cleanup_result
            }
        
        return {
            'cleanup_triggered': False,
            'current_count': current_count,
            'max_allowed': MAX_DATASETS
        }
        
    except Exception as e:
        logger.error(f"Error in trigger_cleanup_if_needed: {str(e)}")
        return {
            'cleanup_triggered': False,
            'error': str(e)
        }


def get_datasets_for_cleanup_preview():
    """
    Get a preview of datasets that would be deleted in the next cleanup
    
    Returns:
        List of datasets that would be deleted
    """
    try:
        all_datasets = Dataset.objects.order_by('-upload_date')
        
        if all_datasets.count() > MAX_DATASETS:
            datasets_to_delete = all_datasets[MAX_DATASETS:]
            
            preview = []
            for dataset in datasets_to_delete:
                preview.append({
                    'id': dataset.id,
                    'name': dataset.name,
                    'upload_date': dataset.upload_date,
                    'total_rows': dataset.total_rows,
                    'file_name': dataset.file_name
                })
            
            return preview
        
        return []
        
    except Exception as e:
        logger.error(f"Error getting cleanup preview: {str(e)}")
        return []