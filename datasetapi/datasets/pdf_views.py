"""
PDF report generation views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.conf import settings
import os
import logging

from .models import Dataset
from .pdf_utils import generate_dataset_pdf_report

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf_report(request, dataset_id):
    """
    Generate and download PDF report for a dataset
    
    GET /api/reports/pdf/{dataset_id}/
    
    Returns:
        PDF file download or error response
    """
    try:
        # Get the dataset
        dataset = get_object_or_404(Dataset, id=dataset_id, is_processed=True)
        
        # Check if dataset has summary statistics
        if not hasattr(dataset, 'summary'):
            return Response({
                'error': 'Dataset does not have summary statistics available',
                'dataset_id': dataset_id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate PDF report
        pdf_buffer, filename = generate_dataset_pdf_report(dataset)
        
        # Create HTTP response with PDF
        response = HttpResponse(
            pdf_buffer.getvalue(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_buffer.getvalue())
        
        logger.info(f"Generated PDF report for dataset {dataset_id}: {filename}")
        
        return response
        
    except Dataset.DoesNotExist:
        return Response({
            'error': 'Dataset not found or not processed',
            'dataset_id': dataset_id
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Error generating PDF report for dataset {dataset_id}: {str(e)}")
        return Response({
            'error': 'Failed to generate PDF report',
            'details': str(e),
            'dataset_id': dataset_id
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preview_pdf_report(request, dataset_id):
    """
    Get information about what would be included in the PDF report
    
    GET /api/reports/preview/{dataset_id}/
    
    Returns:
        JSON with report preview information
    """
    try:
        # Get the dataset
        dataset = get_object_or_404(Dataset, id=dataset_id, is_processed=True)
        
        # Check if dataset has summary statistics
        if not hasattr(dataset, 'summary'):
            return Response({
                'error': 'Dataset does not have summary statistics available',
                'dataset_id': dataset_id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        summary = dataset.summary
        
        # Prepare preview information
        preview_info = {
            'dataset_info': {
                'id': dataset.id,
                'name': dataset.name,
                'description': dataset.description,
                'file_name': dataset.file_name,
                'file_type': dataset.file_type,
                'upload_date': dataset.upload_date,
                'total_rows': dataset.total_rows,
                'total_columns': dataset.total_columns
            },
            'report_sections': {
                'title_page': True,
                'dataset_overview': True,
                'operational_metrics': bool(summary.avg_flowrate or summary.avg_pressure or summary.avg_temperature),
                'equipment_analysis': bool(summary.equipment_type_distribution),
                'data_quality_metrics': bool(summary.statistics_data and summary.statistics_data.get('data_quality')),
                'column_analysis': dataset.columns.exists()
            },
            'metrics_included': {
                'total_records': summary.total_records,
                'avg_flowrate': summary.avg_flowrate,
                'avg_pressure': summary.avg_pressure,
                'avg_temperature': summary.avg_temperature,
                'equipment_types': len(summary.equipment_type_distribution) if summary.equipment_type_distribution else 0,
                'missing_values': summary.missing_values_count,
                'columns_analyzed': dataset.columns.count()
            },
            'estimated_pages': 3 + (1 if summary.equipment_type_distribution else 0) + (1 if dataset.columns.count() > 10 else 0),
            'pdf_filename': f"dataset_report_{dataset.name}_{dataset.id}.pdf"
        }
        
        return Response(preview_info, status=status.HTTP_200_OK)
        
    except Dataset.DoesNotExist:
        return Response({
            'error': 'Dataset not found or not processed',
            'dataset_id': dataset_id
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Error generating PDF preview for dataset {dataset_id}: {str(e)}")
        return Response({
            'error': 'Failed to generate PDF preview',
            'details': str(e),
            'dataset_id': dataset_id
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_available_reports(request):
    """
    List all datasets that have PDF reports available
    
    GET /api/reports/available/
    
    Returns:
        JSON list of datasets with report availability
    """
    try:
        # Get all processed datasets with summary statistics
        datasets_with_reports = Dataset.objects.filter(
            is_processed=True,
            summary__isnull=False
        ).select_related('summary').order_by('-upload_date')
        
        reports_list = []
        for dataset in datasets_with_reports:
            reports_list.append({
                'dataset_id': dataset.id,
                'name': dataset.name,
                'description': dataset.description,
                'upload_date': dataset.upload_date,
                'total_rows': dataset.total_rows,
                'total_columns': dataset.total_columns,
                'has_operational_metrics': bool(
                    dataset.summary.avg_flowrate or 
                    dataset.summary.avg_pressure or 
                    dataset.summary.avg_temperature
                ),
                'has_equipment_analysis': bool(dataset.summary.equipment_type_distribution),
                'pdf_url': f'/api/reports/pdf/{dataset.id}/',
                'preview_url': f'/api/reports/preview/{dataset.id}/'
            })
        
        return Response({
            'count': len(reports_list),
            'reports': reports_list
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing available reports: {str(e)}")
        return Response({
            'error': 'Failed to list available reports',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_generate_reports(request):
    """
    Generate PDF reports for multiple datasets
    
    POST /api/reports/batch/
    {
        "dataset_ids": [1, 2, 3]
    }
    
    Returns:
        JSON with batch generation results
    """
    try:
        dataset_ids = request.data.get('dataset_ids', [])
        
        if not dataset_ids:
            return Response({
                'error': 'No dataset IDs provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(dataset_ids) > 10:  # Limit batch size
            return Response({
                'error': 'Maximum 10 datasets allowed per batch'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        results = []
        successful_count = 0
        failed_count = 0
        
        for dataset_id in dataset_ids:
            try:
                dataset = Dataset.objects.get(id=dataset_id, is_processed=True)
                
                if not hasattr(dataset, 'summary'):
                    results.append({
                        'dataset_id': dataset_id,
                        'status': 'failed',
                        'error': 'No summary statistics available'
                    })
                    failed_count += 1
                    continue
                
                # Generate PDF (in a real implementation, you might want to do this asynchronously)
                pdf_buffer, filename = generate_dataset_pdf_report(dataset)
                
                results.append({
                    'dataset_id': dataset_id,
                    'status': 'success',
                    'filename': filename,
                    'size_bytes': len(pdf_buffer.getvalue()),
                    'download_url': f'/api/reports/pdf/{dataset_id}/'
                })
                successful_count += 1
                
            except Dataset.DoesNotExist:
                results.append({
                    'dataset_id': dataset_id,
                    'status': 'failed',
                    'error': 'Dataset not found or not processed'
                })
                failed_count += 1
                
            except Exception as e:
                results.append({
                    'dataset_id': dataset_id,
                    'status': 'failed',
                    'error': str(e)
                })
                failed_count += 1
        
        return Response({
            'batch_summary': {
                'total_requested': len(dataset_ids),
                'successful': successful_count,
                'failed': failed_count
            },
            'results': results
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in batch report generation: {str(e)}")
        return Response({
            'error': 'Batch report generation failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)