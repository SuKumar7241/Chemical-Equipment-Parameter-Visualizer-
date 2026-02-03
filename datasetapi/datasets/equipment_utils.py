"""
Equipment-specific data processing utilities
Handles CSV validation, parsing, and analysis for equipment data
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from django.core.exceptions import ValidationError


# Required columns for equipment CSV files
REQUIRED_COLUMNS = {
    'equipment_id': ['equipment_id', 'id', 'equipment_number'],
    'equipment_type': ['equipment_type', 'type', 'category', 'equipment_category'],
    'flowrate': ['flowrate', 'flow_rate', 'flow', 'rate'],
    'pressure': ['pressure', 'press', 'psi', 'bar'],
    'temperature': ['temperature', 'temp', 'celsius', 'fahrenheit']
}

# Optional columns that might be present
OPTIONAL_COLUMNS = {
    'timestamp': ['timestamp', 'date', 'datetime', 'time'],
    'location': ['location', 'site', 'facility', 'plant'],
    'status': ['status', 'state', 'condition'],
    'operator': ['operator', 'technician', 'user']
}


def validate_csv_columns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate that the CSV contains required columns for equipment data
    
    Args:
        df: Pandas DataFrame to validate
        
    Returns:
        Dict containing validation results and column mappings
        
    Raises:
        ValidationError: If required columns are missing
    """
    validation_result = {
        'is_valid': True,
        'column_mapping': {},
        'missing_columns': [],
        'found_columns': list(df.columns),
        'errors': []
    }
    
    # Convert column names to lowercase for case-insensitive matching
    df_columns_lower = [col.lower().strip() for col in df.columns]
    
    # Check for required columns
    for required_field, possible_names in REQUIRED_COLUMNS.items():
        found = False
        for possible_name in possible_names:
            if possible_name.lower() in df_columns_lower:
                # Find the actual column name (with original case)
                actual_column = df.columns[df_columns_lower.index(possible_name.lower())]
                validation_result['column_mapping'][required_field] = actual_column
                found = True
                break
        
        if not found:
            validation_result['missing_columns'].append(required_field)
            validation_result['errors'].append(
                f"Required column '{required_field}' not found. "
                f"Expected one of: {', '.join(possible_names)}"
            )
    
    # Check for optional columns
    for optional_field, possible_names in OPTIONAL_COLUMNS.items():
        for possible_name in possible_names:
            if possible_name.lower() in df_columns_lower:
                actual_column = df.columns[df_columns_lower.index(possible_name.lower())]
                validation_result['column_mapping'][optional_field] = actual_column
                break
    
    # Set validation status
    validation_result['is_valid'] = len(validation_result['missing_columns']) == 0
    
    return validation_result


def clean_and_validate_data(df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Clean and validate the equipment data
    
    Args:
        df: Raw DataFrame
        column_mapping: Mapping of standard names to actual column names
        
    Returns:
        Cleaned DataFrame with standardized column names
    """
    # Create a copy with standardized column names
    cleaned_df = df.copy()
    
    # Rename columns to standard names
    rename_mapping = {v: k for k, v in column_mapping.items()}
    cleaned_df = cleaned_df.rename(columns=rename_mapping)
    
    # Clean numeric columns
    numeric_columns = ['flowrate', 'pressure', 'temperature']
    for col in numeric_columns:
        if col in cleaned_df.columns:
            # Convert to numeric, coercing errors to NaN
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
            
            # Remove negative values for flowrate (if they don't make sense)
            if col == 'flowrate':
                cleaned_df.loc[cleaned_df[col] < 0, col] = np.nan
    
    # Clean equipment_type column
    if 'equipment_type' in cleaned_df.columns:
        cleaned_df['equipment_type'] = cleaned_df['equipment_type'].astype(str).str.strip().str.title()
        # Replace empty strings with NaN
        cleaned_df.loc[cleaned_df['equipment_type'] == '', 'equipment_type'] = np.nan
    
    # Clean equipment_id column
    if 'equipment_id' in cleaned_df.columns:
        cleaned_df['equipment_id'] = cleaned_df['equipment_id'].astype(str).str.strip()
    
    return cleaned_df


def calculate_equipment_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate comprehensive summary statistics for equipment data
    
    Args:
        df: Cleaned DataFrame with standardized column names
        
    Returns:
        Dictionary containing summary statistics
    """
    summary = {
        'total_records': len(df),
        'data_quality': {},
        'equipment_analysis': {},
        'operational_metrics': {},
        'distribution_analysis': {}
    }
    
    # Data Quality Analysis
    summary['data_quality'] = {
        'total_rows': len(df),
        'complete_rows': len(df.dropna()),
        'missing_data_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
        'columns_with_missing_data': df.columns[df.isnull().any()].tolist(),
        'missing_data_by_column': df.isnull().sum().to_dict()
    }
    
    # Equipment Analysis
    if 'equipment_type' in df.columns:
        equipment_counts = df['equipment_type'].value_counts()
        summary['equipment_analysis'] = {
            'total_equipment_types': len(equipment_counts),
            'equipment_type_distribution': equipment_counts.to_dict(),
            'most_common_equipment': equipment_counts.index[0] if len(equipment_counts) > 0 else None,
            'equipment_type_percentages': (equipment_counts / len(df) * 100).round(2).to_dict()
        }
    
    # Operational Metrics
    operational_metrics = {}
    
    # Flowrate analysis
    if 'flowrate' in df.columns:
        flowrate_data = df['flowrate'].dropna()
        if len(flowrate_data) > 0:
            operational_metrics['flowrate'] = {
                'average': float(flowrate_data.mean()),
                'median': float(flowrate_data.median()),
                'std_deviation': float(flowrate_data.std()),
                'min': float(flowrate_data.min()),
                'max': float(flowrate_data.max()),
                'count': int(len(flowrate_data)),
                'missing_count': int(df['flowrate'].isnull().sum())
            }
    
    # Pressure analysis
    if 'pressure' in df.columns:
        pressure_data = df['pressure'].dropna()
        if len(pressure_data) > 0:
            operational_metrics['pressure'] = {
                'average': float(pressure_data.mean()),
                'median': float(pressure_data.median()),
                'std_deviation': float(pressure_data.std()),
                'min': float(pressure_data.min()),
                'max': float(pressure_data.max()),
                'count': int(len(pressure_data)),
                'missing_count': int(df['pressure'].isnull().sum())
            }
    
    # Temperature analysis
    if 'temperature' in df.columns:
        temperature_data = df['temperature'].dropna()
        if len(temperature_data) > 0:
            operational_metrics['temperature'] = {
                'average': float(temperature_data.mean()),
                'median': float(temperature_data.median()),
                'std_deviation': float(temperature_data.std()),
                'min': float(temperature_data.min()),
                'max': float(temperature_data.max()),
                'count': int(len(temperature_data)),
                'missing_count': int(df['temperature'].isnull().sum())
            }
    
    summary['operational_metrics'] = operational_metrics
    
    # Distribution Analysis
    distribution_analysis = {}
    
    # Equipment type vs operational metrics
    if 'equipment_type' in df.columns:
        for metric in ['flowrate', 'pressure', 'temperature']:
            if metric in df.columns:
                metric_by_equipment = df.groupby('equipment_type')[metric].agg(['mean', 'count', 'std']).round(2)
                distribution_analysis[f'{metric}_by_equipment_type'] = metric_by_equipment.to_dict('index')
    
    summary['distribution_analysis'] = distribution_analysis
    
    return summary


def process_equipment_csv(file_obj, file_name: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Process equipment CSV file with validation and analysis
    
    Args:
        file_obj: File object to process
        file_name: Name of the file
        
    Returns:
        Tuple of (cleaned_dataframe, summary_statistics)
        
    Raises:
        ValidationError: If CSV validation fails
        ValueError: If file processing fails
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_obj)
        
        if df.empty:
            raise ValidationError("CSV file is empty")
        
        # Validate columns
        validation_result = validate_csv_columns(df)
        
        if not validation_result['is_valid']:
            error_message = "CSV validation failed:\n" + "\n".join(validation_result['errors'])
            raise ValidationError(error_message)
        
        # Clean and standardize data
        cleaned_df = clean_and_validate_data(df, validation_result['column_mapping'])
        
        # Calculate summary statistics
        summary_stats = calculate_equipment_summary(cleaned_df)
        
        # Add validation info to summary
        summary_stats['validation'] = validation_result
        summary_stats['file_info'] = {
            'filename': file_name,
            'original_columns': list(df.columns),
            'standardized_columns': list(cleaned_df.columns),
            'rows_processed': len(cleaned_df)
        }
        
        return cleaned_df, summary_stats
        
    except pd.errors.EmptyDataError:
        raise ValidationError("CSV file is empty or corrupted")
    except pd.errors.ParserError as e:
        raise ValidationError(f"CSV parsing error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing CSV file: {str(e)}")


def get_equipment_data_preview(df: pd.DataFrame, rows: int = 5) -> Dict[str, Any]:
    """
    Get a preview of the equipment dataset
    
    Args:
        df: DataFrame to preview
        rows: Number of rows to include in preview
        
    Returns:
        Dictionary containing preview data
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
        'total_rows_shown': len(preview_data),
        'total_rows_in_dataset': len(df)
    }