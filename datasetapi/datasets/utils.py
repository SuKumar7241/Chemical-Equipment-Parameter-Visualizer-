import pandas as pd
import numpy as np
import json
from typing import Dict, Any, Tuple
from .models import Dataset, SummaryStatistics, DatasetColumn


def process_uploaded_file(file_obj, file_name: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Process uploaded file and return DataFrame and metadata
    """
    file_extension = file_name.lower().split('.')[-1]
    
    try:
        if file_extension == 'csv':
            df = pd.read_csv(file_obj)
        elif file_extension == 'json':
            df = pd.read_json(file_obj)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(file_obj)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Basic metadata
        metadata = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'column_types': {col: str(df[col].dtype) for col in df.columns}
        }
        
        return df, metadata
        
    except Exception as e:
        raise ValueError(f"Error processing file: {str(e)}")


def calculate_column_statistics(series: pd.Series) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics for a pandas Series
    """
    stats = {
        'name': series.name,
        'type': str(series.dtype),
        'count': int(series.count()),
        'missing_count': int(series.isnull().sum()),
        'unique_count': int(series.nunique()),
    }
    
    # Numeric statistics
    if pd.api.types.is_numeric_dtype(series):
        stats.update({
            'mean': float(series.mean()) if not series.empty else None,
            'median': float(series.median()) if not series.empty else None,
            'std': float(series.std()) if not series.empty else None,
            'min': float(series.min()) if not series.empty else None,
            'max': float(series.max()) if not series.empty else None,
            'q25': float(series.quantile(0.25)) if not series.empty else None,
            'q75': float(series.quantile(0.75)) if not series.empty else None,
        })
    
    # Categorical statistics
    else:
        value_counts = series.value_counts()
        if not value_counts.empty:
            stats.update({
                'most_frequent': str(value_counts.index[0]),
                'frequency': int(value_counts.iloc[0]),
                'top_values': {str(k): int(v) for k, v in value_counts.head(10).items()}
            })
    
    return stats


def generate_summary_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive summary statistics for the entire dataset
    """
    summary = {
        'dataset_info': {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage': int(df.memory_usage(deep=True).sum()),
            'missing_values_total': int(df.isnull().sum().sum())
        },
        'columns': {}
    }
    
    # Calculate statistics for each column
    for column in df.columns:
        summary['columns'][column] = calculate_column_statistics(df[column])
    
    # Overall statistics
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns
    
    summary['summary'] = {
        'numeric_columns_count': len(numeric_columns),
        'categorical_columns_count': len(categorical_columns),
        'total_missing_values': int(df.isnull().sum().sum()),
        'missing_percentage': float((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100)
    }
    
    return summary


def create_dataset_from_upload(file_obj, file_name: str, name: str = None, description: str = None) -> Dataset:
    """
    Create Dataset instance from uploaded file with complete processing
    """
    try:
        # Process the file
        df, metadata = process_uploaded_file(file_obj, file_name)
        
        # Create dataset instance
        dataset = Dataset.objects.create(
            name=name or file_name.split('.')[0],
            description=description or '',
            file_name=file_name,
            file_size=file_obj.size,
            file_type=file_name.lower().split('.')[-1],
            total_rows=metadata['total_rows'],
            total_columns=metadata['total_columns'],
            column_names=metadata['column_names'],
            column_types=metadata['column_types'],
            is_processed=False
        )
        
        # Generate summary statistics
        summary_data = generate_summary_statistics(df)
        
        # Create summary statistics
        summary = SummaryStatistics.objects.create(
            dataset=dataset,
            statistics_data=summary_data,
            numeric_columns_count=summary_data['summary']['numeric_columns_count'],
            categorical_columns_count=summary_data['summary']['categorical_columns_count'],
            missing_values_count=summary_data['summary']['total_missing_values']
        )
        
        # Create column records
        for idx, column in enumerate(df.columns):
            col_stats = summary_data['columns'][column]
            
            column_obj = DatasetColumn.objects.create(
                dataset=dataset,
                name=column,
                data_type=col_stats['type'],
                position=idx,
                non_null_count=col_stats['count'],
                null_count=col_stats['missing_count'],
                unique_count=col_stats['unique_count']
            )
            
            # Add numeric-specific fields
            if pd.api.types.is_numeric_dtype(df[column]):
                column_obj.mean_value = col_stats.get('mean')
                column_obj.median_value = col_stats.get('median')
                column_obj.std_value = col_stats.get('std')
                column_obj.min_value = col_stats.get('min')
                column_obj.max_value = col_stats.get('max')
            else:
                column_obj.most_frequent_value = col_stats.get('most_frequent')
                column_obj.most_frequent_count = col_stats.get('frequency')
            
            column_obj.save()
        
        # Mark as processed
        dataset.is_processed = True
        dataset.save()
        
        return dataset
        
    except Exception as e:
        # If dataset was created but processing failed, mark the error
        if 'dataset' in locals():
            dataset.processing_error = str(e)
            dataset.save()
        raise e


def get_dataset_preview(df: pd.DataFrame, rows: int = 5) -> Dict[str, Any]:
    """
    Get a preview of the dataset (first few rows)
    """
    preview_df = df.head(rows)
    
    # Convert to JSON-serializable format
    preview_data = []
    for _, row in preview_df.iterrows():
        row_data = {}
        for col in preview_df.columns:
            value = row[col]
            # Handle NaN and other non-serializable values
            if pd.isna(value):
                row_data[col] = None
            elif isinstance(value, (np.integer, np.floating)):
                row_data[col] = float(value) if np.isfinite(value) else None
            else:
                row_data[col] = str(value)
        preview_data.append(row_data)
    
    return {
        'columns': preview_df.columns.tolist(),
        'data': preview_data,
        'total_rows_shown': len(preview_data)
    }