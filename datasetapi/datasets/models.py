from django.db import models
from django.contrib.auth.models import User
import json


class Dataset(models.Model):
    """Model for storing dataset metadata and file information"""
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # Size in bytes
    file_type = models.CharField(max_length=50)  # csv, json, xlsx, etc.
    upload_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    # Dataset structure metadata
    total_rows = models.IntegerField(null=True, blank=True)
    total_columns = models.IntegerField(null=True, blank=True)
    column_names = models.JSONField(default=list)  # List of column names
    column_types = models.JSONField(default=dict)  # Dict mapping column names to data types
    
    # Processing status
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.name} ({self.file_name})"


class SummaryStatistics(models.Model):
    """Model for storing summary statistics for each dataset"""
    
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE, related_name='summary')
    
    # Basic statistics
    statistics_data = models.JSONField(default=dict)  # Complete statistics as JSON
    
    # Quick access fields for common statistics
    numeric_columns_count = models.IntegerField(default=0)
    categorical_columns_count = models.IntegerField(default=0)
    missing_values_count = models.IntegerField(default=0)
    
    # Equipment-specific summary fields
    total_records = models.IntegerField(default=0)
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)
    equipment_type_distribution = models.JSONField(default=dict)
    
    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Summary Statistics"
    
    def __str__(self):
        return f"Statistics for {self.dataset.name}"
    
    def get_column_statistics(self, column_name):
        """Get statistics for a specific column"""
        return self.statistics_data.get('columns', {}).get(column_name, {})
    
    def get_numeric_summary(self):
        """Get summary of all numeric columns"""
        numeric_stats = {}
        for col_name, col_stats in self.statistics_data.get('columns', {}).items():
            if col_stats.get('type') in ['int64', 'float64', 'numeric']:
                numeric_stats[col_name] = {
                    'mean': col_stats.get('mean'),
                    'median': col_stats.get('median'),
                    'std': col_stats.get('std'),
                    'min': col_stats.get('min'),
                    'max': col_stats.get('max'),
                    'count': col_stats.get('count'),
                    'missing': col_stats.get('missing_count', 0)
                }
        return numeric_stats
    
    def get_categorical_summary(self):
        """Get summary of all categorical columns"""
        categorical_stats = {}
        for col_name, col_stats in self.statistics_data.get('columns', {}).items():
            if col_stats.get('type') in ['object', 'category', 'string']:
                categorical_stats[col_name] = {
                    'unique_count': col_stats.get('unique_count'),
                    'most_frequent': col_stats.get('most_frequent'),
                    'frequency': col_stats.get('frequency'),
                    'missing': col_stats.get('missing_count', 0)
                }
        return categorical_stats


class DatasetColumn(models.Model):
    """Model for storing detailed information about each column in a dataset"""
    
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='columns')
    
    name = models.CharField(max_length=255)
    data_type = models.CharField(max_length=50)  # pandas dtype
    position = models.IntegerField()  # Column position in the dataset
    
    # Column statistics
    non_null_count = models.IntegerField(default=0)
    null_count = models.IntegerField(default=0)
    unique_count = models.IntegerField(default=0)
    
    # For numeric columns
    mean_value = models.FloatField(null=True, blank=True)
    median_value = models.FloatField(null=True, blank=True)
    std_value = models.FloatField(null=True, blank=True)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    
    # For categorical columns
    most_frequent_value = models.TextField(null=True, blank=True)
    most_frequent_count = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['position']
        unique_together = ['dataset', 'name']
    
    def __str__(self):
        return f"{self.dataset.name} - {self.name} ({self.data_type})"
    
    @property
    def is_numeric(self):
        return self.data_type in ['int64', 'float64', 'int32', 'float32']
    
    @property
    def is_categorical(self):
        return self.data_type in ['object', 'category', 'string']