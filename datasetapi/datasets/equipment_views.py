"""
Equipment-specific API views for CSV upload and data summary
"""
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.utils import timezone
import pandas as pd

from .models import Dataset, SummaryStatistics, DatasetColumn
from .equipment_serializers import (
    EquipmentCSVUploadSerializer, EquipmentSummarySerializer,
    DataSummaryResponseSerializer, EquipmentDataPreviewSerializer,
    CSVValidationResponseSerializer
)
from .equipment_utils import (
    process_equipment_csv, validate_csv_columns, 
    get_equipment_data_preview, clean_and_validate_data
)
from .history_utils import trigger_cleanup_if_needed


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def equipment_csv_upload(request):
    """
    API endpoint for uploading equipment CSV files with validation
    
    POST /api/equipment/upload/
    
    Expected CSV columns (case-insensitive):
    - equipment_id (or id, equipment_number)
    - equipment_type (or type, category, equipment_category)  
    - flowrate (or flow_rate, flow, rate)
    - pressure (or press, psi, bar)
    - temperature (or temp, celsius, fahrenheit)
    
    Optional columns:
    - timestamp, location, status, operator
    
    Returns:
        201: Dataset created successfully with analysis
        400: Validation error or processing failure
    """
    # Check authentication
    if not request.user.is_authenticated:
        return Response({
            'error': 'Authentication required',
            'message': 'Please login to upload datasets'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer = EquipmentCSVUploadSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        file_obj = serializer.validated_data['file']
        name = serializer.validated_data.get('name', file_obj.name.split('.')[0])
        description = serializer.validated_data.get('description', 'Equipment data uploaded via API')
        
        # Process the equipment CSV
        cleaned_df, summary_stats = process_equipment_csv(file_obj, file_obj.name)
        
        # Create dataset instance
        dataset = Dataset.objects.create(
            name=name,
            description=description,
            file_name=file_obj.name,
            file_size=file_obj.size,
            file_type='csv',
            total_rows=len(cleaned_df),
            total_columns=len(cleaned_df.columns),
            column_names=list(cleaned_df.columns),
            column_types={col: str(cleaned_df[col].dtype) for col in cleaned_df.columns},
            is_processed=True
        )
        
        # Extract equipment-specific metrics for quick access
        operational_metrics = summary_stats.get('operational_metrics', {})
        equipment_analysis = summary_stats.get('equipment_analysis', {})
        
        # Ensure JSON serializable data
        import json
        import numpy as np
        
        def make_json_serializable(obj):
            """Convert numpy types to native Python types for JSON serialization"""
            if isinstance(obj, dict):
                return {k: make_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_json_serializable(v) for v in obj]
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif pd.isna(obj):
                return None
            else:
                return obj
        
        try:
            # Clean the summary stats to ensure JSON compatibility
            clean_stats = make_json_serializable(summary_stats)
            # Test JSON serialization
            json.dumps(clean_stats)
            json_stats = clean_stats
        except (TypeError, ValueError) as e:
            # If serialization fails, create a simplified version
            json_stats = {
                'total_records': len(cleaned_df),
                'operational_metrics': make_json_serializable(operational_metrics),
                'equipment_analysis': make_json_serializable(equipment_analysis),
                'data_quality': {
                    'total_rows': len(cleaned_df),
                    'complete_rows': len(cleaned_df.dropna()),
                    'missing_data_percentage': float((cleaned_df.isnull().sum().sum() / (len(cleaned_df) * len(cleaned_df.columns))) * 100)
                },
                'file_info': {
                    'filename': file_obj.name,
                    'rows_processed': len(cleaned_df),
                    'columns_processed': len(cleaned_df.columns)
                }
            }
        
        # Create summary statistics
        summary = SummaryStatistics.objects.create(
            dataset=dataset,
            statistics_data=json_stats,
            numeric_columns_count=len([col for col in cleaned_df.columns if cleaned_df[col].dtype in ['int64', 'float64']]),
            categorical_columns_count=len([col for col in cleaned_df.columns if cleaned_df[col].dtype == 'object']),
            missing_values_count=int(cleaned_df.isnull().sum().sum()),
            total_records=len(cleaned_df),
            avg_flowrate=operational_metrics.get('flowrate', {}).get('average'),
            avg_pressure=operational_metrics.get('pressure', {}).get('average'),
            avg_temperature=operational_metrics.get('temperature', {}).get('average'),
            equipment_type_distribution=make_json_serializable(equipment_analysis.get('equipment_type_distribution', {}))
        )
        
        # Create column records
        for idx, column in enumerate(cleaned_df.columns):
            col_data = cleaned_df[column]
            
            column_obj = DatasetColumn.objects.create(
                dataset=dataset,
                name=column,
                data_type=str(col_data.dtype),
                position=idx,
                non_null_count=int(col_data.count()),
                null_count=int(col_data.isnull().sum()),
                unique_count=int(col_data.nunique())
            )
            
            # Add numeric-specific fields
            if pd.api.types.is_numeric_dtype(col_data):
                if col_data.count() > 0:  # Only if there are non-null values
                    column_obj.mean_value = float(col_data.mean())
                    column_obj.median_value = float(col_data.median())
                    column_obj.std_value = float(col_data.std()) if col_data.std() == col_data.std() else None  # Check for NaN
                    column_obj.min_value = float(col_data.min())
                    column_obj.max_value = float(col_data.max())
            else:
                # Categorical column statistics
                if col_data.count() > 0:
                    value_counts = col_data.value_counts()
                    if len(value_counts) > 0:
                        column_obj.most_frequent_value = str(value_counts.index[0])
                        column_obj.most_frequent_count = int(value_counts.iloc[0])
            
            column_obj.save()
        
        # Trigger cleanup if needed (history management)
        cleanup_result = trigger_cleanup_if_needed()
        
        # Prepare response
        response_data = {
            'dataset_id': dataset.id,
            'name': dataset.name,
            'status': 'success',
            'message': 'Equipment CSV uploaded and processed successfully',
            'summary': {
                'total_records': summary.total_records,
                'columns_processed': len(cleaned_df.columns),
                'equipment_types_found': len(summary.equipment_type_distribution),
                'avg_flowrate': summary.avg_flowrate,
                'avg_pressure': summary.avg_pressure,
                'avg_temperature': summary.avg_temperature
            },
            'validation': summary_stats.get('validation', {}),
            'data_quality': summary_stats.get('data_quality', {}),
            'history_management': cleanup_result
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except ValidationError as e:
        return Response({
            'error': 'CSV validation failed',
            'details': str(e),
            'status': 'validation_error'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': 'Failed to process equipment CSV',
            'details': str(e),
            'status': 'processing_error'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def data_summary(request, dataset_id=None):
    """
    API endpoint for getting equipment data summary
    
    GET /api/equipment/summary/{dataset_id}/
    GET /api/equipment/summary/  (for all datasets combined)
    
    Returns comprehensive summary including:
    - Total record count
    - Average flowrate, pressure, temperature
    - Equipment type distribution
    - Data quality metrics
    - Operational analysis
    """
    try:
        if dataset_id:
            # Get summary for specific dataset
            try:
                dataset = Dataset.objects.get(id=dataset_id, is_processed=True)
                summary = dataset.summary
                
                # Prepare detailed response
                response_data = {
                    'total_record_count': summary.total_records,
                    'average_flowrate': summary.avg_flowrate,
                    'average_pressure': summary.avg_pressure,
                    'average_temperature': summary.avg_temperature,
                    'equipment_type_distribution': summary.equipment_type_distribution,
                    'operational_metrics': summary.statistics_data.get('operational_metrics', {}),
                    'data_quality': summary.statistics_data.get('data_quality', {}),
                    'equipment_analysis': summary.statistics_data.get('equipment_analysis', {}),
                    'dataset_info': {
                        'id': dataset.id,
                        'name': dataset.name,
                        'description': dataset.description,
                        'upload_date': dataset.upload_date,
                        'total_rows': dataset.total_rows,
                        'total_columns': dataset.total_columns
                    },
                    'analysis_timestamp': summary.updated_date
                }
                
                serializer = DataSummaryResponseSerializer(response_data)
                return Response(serializer.data, status=status.HTTP_200_OK)
                
            except Dataset.DoesNotExist:
                return Response({
                    'error': 'Dataset not found or not processed',
                    'dataset_id': dataset_id
                }, status=status.HTTP_404_NOT_FOUND)
                
        else:
            # Get combined summary for all datasets
            summaries = SummaryStatistics.objects.filter(dataset__is_processed=True)
            
            if not summaries.exists():
                return Response({
                    'error': 'No processed datasets found',
                    'total_datasets': 0
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Calculate combined metrics
            total_records = sum(s.total_records for s in summaries)
            
            # Calculate weighted averages for operational metrics
            flowrate_sum = sum(s.avg_flowrate * s.total_records for s in summaries if s.avg_flowrate is not None)
            pressure_sum = sum(s.avg_pressure * s.total_records for s in summaries if s.avg_pressure is not None)
            temperature_sum = sum(s.avg_temperature * s.total_records for s in summaries if s.avg_temperature is not None)
            
            flowrate_count = sum(s.total_records for s in summaries if s.avg_flowrate is not None)
            pressure_count = sum(s.total_records for s in summaries if s.avg_pressure is not None)
            temperature_count = sum(s.total_records for s in summaries if s.avg_temperature is not None)
            
            # Combine equipment type distributions
            combined_equipment_dist = {}
            for summary in summaries:
                for eq_type, count in summary.equipment_type_distribution.items():
                    combined_equipment_dist[eq_type] = combined_equipment_dist.get(eq_type, 0) + count
            
            response_data = {
                'total_record_count': total_records,
                'average_flowrate': flowrate_sum / flowrate_count if flowrate_count > 0 else None,
                'average_pressure': pressure_sum / pressure_count if pressure_count > 0 else None,
                'average_temperature': temperature_sum / temperature_count if temperature_count > 0 else None,
                'equipment_type_distribution': combined_equipment_dist,
                'operational_metrics': {
                    'datasets_included': len(summaries),
                    'total_equipment_types': len(combined_equipment_dist)
                },
                'data_quality': {
                    'total_datasets': len(summaries),
                    'total_records_across_datasets': total_records
                },
                'equipment_analysis': {
                    'combined_equipment_distribution': combined_equipment_dist,
                    'most_common_equipment_overall': max(combined_equipment_dist.items(), key=lambda x: x[1])[0] if combined_equipment_dist else None
                },
                'dataset_info': {
                    'datasets_included': [{'id': s.dataset.id, 'name': s.dataset.name} for s in summaries]
                },
                'analysis_timestamp': timezone.now()
            }
            
            serializer = DataSummaryResponseSerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'error': 'Failed to generate data summary',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def validate_csv(request):
    """
    API endpoint for validating CSV structure without uploading
    
    POST /api/equipment/validate/
    
    Returns validation results and data preview
    """
    try:
        if 'file' not in request.FILES:
            return Response({
                'error': 'No file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.FILES['file']
        
        if not file_obj.name.lower().endswith('.csv'):
            return Response({
                'error': 'Only CSV files are supported'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Read CSV for validation
        df = pd.read_csv(file_obj)
        
        if df.empty:
            return Response({
                'error': 'CSV file is empty'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate columns
        validation_result = validate_csv_columns(df)
        
        # Get data preview if validation passes
        preview_data = None
        if validation_result['is_valid']:
            cleaned_df = clean_and_validate_data(df, validation_result['column_mapping'])
            preview_data = get_equipment_data_preview(cleaned_df, rows=5)
        
        # Prepare response
        response_data = {
            'is_valid': validation_result['is_valid'],
            'column_mapping': validation_result['column_mapping'],
            'missing_columns': validation_result['missing_columns'],
            'found_columns': validation_result['found_columns'],
            'errors': validation_result['errors'],
            'file_info': {
                'filename': file_obj.name,
                'size': file_obj.size,
                'rows': len(df),
                'columns': len(df.columns)
            }
        }
        
        if preview_data:
            response_data['data_preview'] = preview_data
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except pd.errors.EmptyDataError:
        return Response({
            'error': 'CSV file is empty or corrupted'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except pd.errors.ParserError as e:
        return Response({
            'error': f'CSV parsing error: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': f'Failed to validate CSV: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def equipment_data_preview(request, dataset_id):
    """
    API endpoint for getting equipment data preview
    
    GET /api/equipment/preview/{dataset_id}/
    """
    try:
        dataset = Dataset.objects.get(id=dataset_id, is_processed=True)
        
        # This is a simplified preview since we don't store raw data
        # In a real implementation, you might want to store sample data or re-read the file
        response_data = {
            'dataset_info': {
                'id': dataset.id,
                'name': dataset.name,
                'total_rows': dataset.total_rows,
                'total_columns': dataset.total_columns,
                'columns': dataset.column_names
            },
            'column_types': dataset.column_types,
            'summary': {
                'avg_flowrate': dataset.summary.avg_flowrate,
                'avg_pressure': dataset.summary.avg_pressure,
                'avg_temperature': dataset.summary.avg_temperature,
                'equipment_types': list(dataset.summary.equipment_type_distribution.keys())
            },
            'note': 'Full data preview requires file storage implementation. This shows metadata and summary statistics.'
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Dataset.DoesNotExist:
        return Response({
            'error': 'Dataset not found or not processed'
        }, status=status.HTTP_404_NOT_FOUND)