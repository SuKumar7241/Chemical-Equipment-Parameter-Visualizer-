from django.contrib import admin
from .models import Dataset, SummaryStatistics, DatasetColumn


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_name', 'file_type', 'total_rows', 'total_columns', 'is_processed', 'upload_date']
    list_filter = ['file_type', 'is_processed', 'upload_date']
    search_fields = ['name', 'file_name', 'description']
    readonly_fields = ['upload_date', 'updated_date', 'file_size', 'total_rows', 'total_columns', 'column_names', 'column_types']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'file_name', 'file_type', 'file_size')
        }),
        ('Dataset Structure', {
            'fields': ('total_rows', 'total_columns', 'column_names', 'column_types')
        }),
        ('Processing Status', {
            'fields': ('is_processed', 'processing_error')
        }),
        ('Timestamps', {
            'fields': ('upload_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SummaryStatistics)
class SummaryStatisticsAdmin(admin.ModelAdmin):
    list_display = ['dataset', 'numeric_columns_count', 'categorical_columns_count', 'missing_values_count', 'created_date']
    list_filter = ['created_date', 'updated_date']
    search_fields = ['dataset__name']
    readonly_fields = ['created_date', 'updated_date']
    
    fieldsets = (
        ('Dataset', {
            'fields': ('dataset',)
        }),
        ('Summary Counts', {
            'fields': ('numeric_columns_count', 'categorical_columns_count', 'missing_values_count')
        }),
        ('Detailed Statistics', {
            'fields': ('statistics_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DatasetColumn)
class DatasetColumnAdmin(admin.ModelAdmin):
    list_display = ['dataset', 'name', 'data_type', 'position', 'non_null_count', 'null_count', 'unique_count']
    list_filter = ['data_type', 'dataset__file_type']
    search_fields = ['name', 'dataset__name']
    ordering = ['dataset', 'position']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('dataset', 'name', 'data_type', 'position')
        }),
        ('General Statistics', {
            'fields': ('non_null_count', 'null_count', 'unique_count')
        }),
        ('Numeric Statistics', {
            'fields': ('mean_value', 'median_value', 'std_value', 'min_value', 'max_value'),
            'classes': ('collapse',)
        }),
        ('Categorical Statistics', {
            'fields': ('most_frequent_value', 'most_frequent_count'),
            'classes': ('collapse',)
        }),
    )