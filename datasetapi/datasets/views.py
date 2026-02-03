from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import pandas as pd

from .models import Dataset, SummaryStatistics, DatasetColumn
from .serializers import (
    DatasetSerializer, DatasetListSerializer, DatasetUploadSerializer,
    SummaryStatisticsSerializer, DatasetColumnSerializer
)
from .utils import create_dataset_from_upload, process_uploaded_file, get_dataset_preview


class DatasetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing datasets
    """
    queryset = Dataset.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DatasetListSerializer
        elif self.action == 'upload':
            return DatasetUploadSerializer
        return DatasetSerializer
    
    def list(self, request):
        """List all datasets with basic information"""
        datasets = self.get_queryset()
        serializer = DatasetListSerializer(datasets, many=True)
        return Response({
            'count': datasets.count(),
            'results': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """Get detailed information about a specific dataset"""
        dataset = get_object_or_404(Dataset, pk=pk)
        serializer = DatasetSerializer(dataset)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload and process a new dataset"""
        serializer = DatasetUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                file_obj = serializer.validated_data['file']
                name = serializer.validated_data.get('name')
                description = serializer.validated_data.get('description')
                
                # Create dataset with processing
                dataset = create_dataset_from_upload(
                    file_obj=file_obj,
                    file_name=file_obj.name,
                    name=name,
                    description=description
                )
                
                # Return the created dataset
                response_serializer = DatasetSerializer(dataset)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response(
                    {'error': f'Failed to process file: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get detailed statistics for a dataset"""
        dataset = get_object_or_404(Dataset, pk=pk)
        
        if not dataset.is_processed:
            return Response(
                {'error': 'Dataset is not yet processed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            summary = dataset.summary
            serializer = SummaryStatisticsSerializer(summary)
            return Response(serializer.data)
        except SummaryStatistics.DoesNotExist:
            return Response(
                {'error': 'Statistics not available for this dataset'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def columns(self, request, pk=None):
        """Get detailed information about dataset columns"""
        dataset = get_object_or_404(Dataset, pk=pk)
        columns = dataset.columns.all()
        serializer = DatasetColumnSerializer(columns, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Get a preview of the dataset (first few rows)"""
        dataset = get_object_or_404(Dataset, pk=pk)
        
        if not dataset.is_processed:
            return Response(
                {'error': 'Dataset is not yet processed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # This is a simplified preview - in a real application, 
        # you might want to store sample data or re-read the file
        return Response({
            'message': 'Preview functionality would require file storage implementation',
            'columns': dataset.column_names,
            'total_rows': dataset.total_rows,
            'total_columns': dataset.total_columns
        })
    
    @action(detail=True, methods=['delete'])
    def delete_dataset(self, request, pk=None):
        """Delete a dataset and all associated data"""
        dataset = get_object_or_404(Dataset, pk=pk)
        dataset_name = dataset.name
        dataset.delete()
        
        return Response({
            'message': f'Dataset "{dataset_name}" has been deleted successfully'
        }, status=status.HTTP_200_OK)


class SummaryStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for accessing summary statistics
    """
    queryset = SummaryStatistics.objects.all()
    serializer_class = SummaryStatisticsSerializer
    
    @action(detail=True, methods=['get'])
    def numeric_summary(self, request, pk=None):
        """Get summary of numeric columns only"""
        summary = get_object_or_404(SummaryStatistics, pk=pk)
        return Response(summary.get_numeric_summary())
    
    @action(detail=True, methods=['get'])
    def categorical_summary(self, request, pk=None):
        """Get summary of categorical columns only"""
        summary = get_object_or_404(SummaryStatistics, pk=pk)
        return Response(summary.get_categorical_summary())


class DatasetColumnViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for accessing dataset column information
    """
    queryset = DatasetColumn.objects.all()
    serializer_class = DatasetColumnSerializer
    
    def get_queryset(self):
        queryset = DatasetColumn.objects.all()
        dataset_id = self.request.query_params.get('dataset', None)
        if dataset_id is not None:
            queryset = queryset.filter(dataset_id=dataset_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_dataset(self, request):
        """Get columns for a specific dataset"""
        dataset_id = request.query_params.get('dataset_id')
        if not dataset_id:
            return Response(
                {'error': 'dataset_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        columns = DatasetColumn.objects.filter(dataset_id=dataset_id)
        serializer = DatasetColumnSerializer(columns, many=True)
        return Response(serializer.data)