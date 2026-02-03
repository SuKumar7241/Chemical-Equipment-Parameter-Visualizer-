"""
Data Summary API Views
Provides comprehensive data summaries using Pandas calculations
"""

import pandas as pd
import os
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Dataset, SummaryStatistics
from .serializers import DataSummarySerializer


@api_view(['GET'])
def data_summary_api(request, dataset_id):
    """
    Data Summary API
    
    Returns:
    1. Total record count
    2. Average values for flowrate, pressure, temperature
    3. Equipment type distribution (count per equipment type)
    
    All calculations done using Pandas from uploaded CSV data.
    """
    try:
        # Get dataset
        dataset = Dataset.objects.get(id=dataset_id)
        
        # Check if dataset is processed
        if not dataset.is_processed:
            return Response({
                'error': 'Dataset not yet processed',
                'message': 'Please wait for dataset processing to complete'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Load CSV data using Pandas
        csv_path = os.path.join(settings.MEDIA_ROOT, 'datasets', dataset.file_name)
        
        if not os.path.exists(csv_path):
            return Response({
                'error': 'Dataset file not found',
                'message': 'The original CSV file is no longer available'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Read CSV with Pandas
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            return Response({
                'error': 'Failed to read CSV file',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Calculate summary data using Pandas
        summary_data = calculate_data_summary(df)
        
        # Store/update summary in database
        summary_stats, created = SummaryStatistics.objects.get_or_create(
            dataset=dataset,
            defaults={
                'total_records': summary_data['total_records'],
                'avg_flowrate': summary_data['averages'].get('flowrate'),
                'avg_pressure': summary_data['averages'].get('pressure'),
                'avg_temperature': summary_data['averages'].get('temperature'),
                'equipment_type_distribution': summary_data['equipment_type_distribution']
            }
        )
        
        if not created:
            # Update existing summary
            summary_stats.total_records = summary_data['total_records']
            summary_stats.avg_flowrate = summary_data['averages'].get('flowrate')
            summary_stats.avg_pressure = summary_data['averages'].get('pressure')
            summary_stats.avg_temperature = summary_data['averages'].get('temperature')
            summary_stats.equipment_type_distribution = summary_data['equipment_type_distribution']
            summary_stats.save()
        
        # Serialize and return response
        serializer = DataSummarySerializer(summary_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Dataset.DoesNotExist:
        return Response({
            'error': 'Dataset not found',
            'message': f'Dataset with ID {dataset_id} does not exist'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def calculate_data_summary(df):
    """
    Calculate data summary using Pandas
    
    Args:
        df (pandas.DataFrame): The dataset DataFrame
        
    Returns:
        dict: Summary data including total records, averages, and equipment distribution
    """
    summary = {
        'total_records': 0,
        'averages': {
            'flowrate': None,
            'pressure': None,
            'temperature': None
        },
        'equipment_type_distribution': {}
    }
    
    # 1. Total record count
    summary['total_records'] = len(df)
    
    # 2. Calculate averages for flowrate, pressure, temperature
    # Handle different possible column names (case-insensitive)
    target_columns = {
        'flowrate': ['flowrate', 'flow_rate', 'flow', 'rate'],
        'pressure': ['pressure', 'press', 'psi', 'bar'],
        'temperature': ['temperature', 'temp', 'celsius', 'fahrenheit']
    }
    
    for metric, possible_names in target_columns.items():
        column_found = None
        
        # Find matching column (case-insensitive)
        for col in df.columns:
            if col.lower() in [name.lower() for name in possible_names]:
                column_found = col
                break
        
        if column_found is not None:
            try:
                # Convert to numeric, handling invalid values gracefully
                numeric_series = pd.to_numeric(df[column_found], errors='coerce')
                
                # Calculate average, excluding NaN values
                if not numeric_series.isna().all():
                    avg_value = numeric_series.mean()
                    summary['averages'][metric] = round(float(avg_value), 2)
                    
            except Exception as e:
                print(f"Error calculating average for {metric}: {e}")
                summary['averages'][metric] = None
    
    # 3. Equipment type distribution
    # Look for equipment type column (case-insensitive)
    equipment_columns = ['equipment_type', 'equipment', 'type', 'device_type', 'machine_type']
    equipment_column = None
    
    for col in df.columns:
        if col.lower() in [name.lower() for name in equipment_columns]:
            equipment_column = col
            break
    
    if equipment_column is not None:
        try:
            # Get value counts for equipment types
            equipment_counts = df[equipment_column].value_counts()
            
            # Convert to dictionary, handling NaN values
            summary['equipment_type_distribution'] = {}
            for equipment_type, count in equipment_counts.items():
                if pd.notna(equipment_type):  # Exclude NaN values
                    summary['equipment_type_distribution'][str(equipment_type)] = int(count)
                    
        except Exception as e:
            print(f"Error calculating equipment distribution: {e}")
            summary['equipment_type_distribution'] = {}
    
    return summary


@api_view(['GET'])
def dataset_summary_list(request):
    """
    List all dataset summaries
    
    Returns summaries for all processed datasets
    """
    try:
        summaries = SummaryStatistics.objects.select_related('dataset').all()
        
        response_data = []
        for summary in summaries:
            response_data.append({
                'dataset_id': summary.dataset.id,
                'dataset_name': summary.dataset.name,
                'total_records': summary.total_records,
                'averages': {
                    'flowrate': summary.avg_flowrate,
                    'pressure': summary.avg_pressure,
                    'temperature': summary.avg_temperature
                },
                'equipment_type_distribution': summary.equipment_type_distribution,
                'last_updated': summary.updated_date.isoformat()
            })
        
        return Response({
            'count': len(response_data),
            'summaries': response_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)