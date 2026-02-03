"""
Equipment-specific serializers for CSV upload and data summary APIs
"""
from rest_framework import serializers
from .models import Dataset, SummaryStatistics


class EquipmentCSVUploadSerializer(serializers.Serializer):
    """
    Serializer for equipment CSV file upload with validation
    """
    file = serializers.FileField()
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    
    def validate_file(self, value):
        """Validate uploaded CSV file"""
        # Check file size (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        # Check file extension
        if not value.name.lower().endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are supported for equipment data")
        
        return value


class EquipmentSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for equipment data summary with operational metrics
    """
    operational_summary = serializers.SerializerMethodField()
    equipment_distribution = serializers.SerializerMethodField()
    data_quality_metrics = serializers.SerializerMethodField()
    
    class Meta:
        model = SummaryStatistics
        fields = [
            'id', 'total_records', 'avg_flowrate', 'avg_pressure', 
            'avg_temperature', 'equipment_type_distribution',
            'created_date', 'updated_date', 'operational_summary',
            'equipment_distribution', 'data_quality_metrics'
        ]
        read_only_fields = ['id', 'created_date', 'updated_date']
    
    def get_operational_summary(self, obj):
        """Get operational metrics summary"""
        stats_data = obj.statistics_data
        operational_metrics = stats_data.get('operational_metrics', {})
        
        summary = {}
        for metric in ['flowrate', 'pressure', 'temperature']:
            if metric in operational_metrics:
                summary[metric] = {
                    'average': operational_metrics[metric].get('average'),
                    'min': operational_metrics[metric].get('min'),
                    'max': operational_metrics[metric].get('max'),
                    'count': operational_metrics[metric].get('count'),
                    'missing_count': operational_metrics[metric].get('missing_count', 0)
                }
        
        return summary
    
    def get_equipment_distribution(self, obj):
        """Get equipment type distribution with percentages"""
        stats_data = obj.statistics_data
        equipment_analysis = stats_data.get('equipment_analysis', {})
        
        return {
            'total_types': equipment_analysis.get('total_equipment_types', 0),
            'distribution': equipment_analysis.get('equipment_type_distribution', {}),
            'percentages': equipment_analysis.get('equipment_type_percentages', {}),
            'most_common': equipment_analysis.get('most_common_equipment')
        }
    
    def get_data_quality_metrics(self, obj):
        """Get data quality metrics"""
        stats_data = obj.statistics_data
        data_quality = stats_data.get('data_quality', {})
        
        return {
            'total_rows': data_quality.get('total_rows', 0),
            'complete_rows': data_quality.get('complete_rows', 0),
            'missing_data_percentage': data_quality.get('missing_data_percentage', 0),
            'columns_with_missing_data': data_quality.get('columns_with_missing_data', [])
        }


class DataSummaryResponseSerializer(serializers.Serializer):
    """
    Serializer for data summary API response
    """
    total_record_count = serializers.IntegerField()
    average_flowrate = serializers.FloatField(allow_null=True)
    average_pressure = serializers.FloatField(allow_null=True)
    average_temperature = serializers.FloatField(allow_null=True)
    equipment_type_distribution = serializers.DictField()
    
    # Additional detailed metrics
    operational_metrics = serializers.DictField()
    data_quality = serializers.DictField()
    equipment_analysis = serializers.DictField()
    
    # Metadata
    dataset_info = serializers.DictField()
    analysis_timestamp = serializers.DateTimeField()


class EquipmentDataPreviewSerializer(serializers.Serializer):
    """
    Serializer for equipment data preview
    """
    columns = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.DictField())
    total_rows_shown = serializers.IntegerField()
    total_rows_in_dataset = serializers.IntegerField()
    
    # Column information
    column_types = serializers.DictField()
    required_columns_found = serializers.ListField(child=serializers.CharField())
    optional_columns_found = serializers.ListField(child=serializers.CharField())


class CSVValidationResponseSerializer(serializers.Serializer):
    """
    Serializer for CSV validation response
    """
    is_valid = serializers.BooleanField()
    column_mapping = serializers.DictField()
    missing_columns = serializers.ListField(child=serializers.CharField())
    found_columns = serializers.ListField(child=serializers.CharField())
    errors = serializers.ListField(child=serializers.CharField())
    
    # Additional validation info
    file_info = serializers.DictField()
    data_preview = EquipmentDataPreviewSerializer(required=False)