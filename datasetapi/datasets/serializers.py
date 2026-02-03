from rest_framework import serializers
from .models import Dataset, SummaryStatistics, DatasetColumn


class DatasetColumnSerializer(serializers.ModelSerializer):
    """Serializer for dataset columns"""
    
    class Meta:
        model = DatasetColumn
        fields = [
            'id', 'name', 'data_type', 'position', 'non_null_count', 
            'null_count', 'unique_count', 'mean_value', 'median_value', 
            'std_value', 'min_value', 'max_value', 'most_frequent_value', 
            'most_frequent_count', 'is_numeric', 'is_categorical'
        ]
        read_only_fields = ['id']


class SummaryStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for summary statistics"""
    
    numeric_summary = serializers.SerializerMethodField()
    categorical_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = SummaryStatistics
        fields = [
            'id', 'statistics_data', 'numeric_columns_count', 
            'categorical_columns_count', 'missing_values_count',
            'created_date', 'updated_date', 'numeric_summary', 'categorical_summary'
        ]
        read_only_fields = ['id', 'created_date', 'updated_date']
    
    def get_numeric_summary(self, obj):
        return obj.get_numeric_summary()
    
    def get_categorical_summary(self, obj):
        return obj.get_categorical_summary()


class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for datasets"""
    
    summary = SummaryStatisticsSerializer(read_only=True)
    columns = DatasetColumnSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'description', 'file_name', 'file_size', 
            'file_type', 'upload_date', 'updated_date', 'total_rows', 
            'total_columns', 'column_names', 'column_types', 
            'is_processed', 'processing_error', 'summary', 'columns'
        ]
        read_only_fields = [
            'id', 'upload_date', 'updated_date', 'file_size', 
            'total_rows', 'total_columns', 'column_names', 
            'column_types', 'is_processed', 'processing_error'
        ]


class DatasetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for dataset list view"""
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'description', 'file_name', 'file_size', 
            'file_type', 'upload_date', 'total_rows', 'total_columns', 
            'is_processed'
        ]
        read_only_fields = ['id', 'upload_date', 'file_size', 'total_rows', 'total_columns', 'is_processed']


class DatasetUploadSerializer(serializers.Serializer):
    """Serializer for dataset file upload"""
    
    file = serializers.FileField()
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    
    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file size (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        # Check file extension
        allowed_extensions = ['.csv', '.json', '.xlsx', '.xls']
        file_extension = value.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        return value


class DataSummarySerializer(serializers.Serializer):
    """Serializer for Data Summary API response"""
    
    total_records = serializers.IntegerField()
    averages = serializers.DictField(
        child=serializers.FloatField(allow_null=True),
        help_text="Average values for flowrate, pressure, temperature"
    )
    equipment_type_distribution = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Count per equipment type"
    )
    
    def to_representation(self, instance):
        """Custom representation to ensure clean JSON structure"""
        data = super().to_representation(instance)
        
        # Ensure averages has the required keys
        if 'averages' not in data:
            data['averages'] = {}
        
        required_avg_keys = ['flowrate', 'pressure', 'temperature']
        for key in required_avg_keys:
            if key not in data['averages']:
                data['averages'][key] = None
        
        # Ensure equipment_type_distribution is present
        if 'equipment_type_distribution' not in data:
            data['equipment_type_distribution'] = {}
        
        return data