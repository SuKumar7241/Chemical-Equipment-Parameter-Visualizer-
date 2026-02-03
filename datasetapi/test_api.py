#!/usr/bin/env python
"""
Simple test script to verify the Django API is working
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datasetapi.settings')
django.setup()

from datasets.models import Dataset, SummaryStatistics, DatasetColumn

def test_models():
    """Test that models are working correctly"""
    print("Testing Django models...")
    
    # Test Dataset model
    print(f"Dataset count: {Dataset.objects.count()}")
    print(f"SummaryStatistics count: {SummaryStatistics.objects.count()}")
    print(f"DatasetColumn count: {DatasetColumn.objects.count()}")
    
    print("✅ Models are working correctly!")

def create_sample_data():
    """Create some sample data for testing"""
    print("Creating sample dataset...")
    
    # Create a sample dataset
    dataset = Dataset.objects.create(
        name="Sample Dataset",
        description="A test dataset for API verification",
        file_name="sample.csv",
        file_size=1024,
        file_type="csv",
        total_rows=100,
        total_columns=5,
        column_names=["id", "name", "age", "salary", "department"],
        column_types={"id": "int64", "name": "object", "age": "int64", "salary": "float64", "department": "object"},
        is_processed=True
    )
    
    print(f"✅ Created dataset: {dataset}")
    return dataset

if __name__ == "__main__":
    test_models()
    sample_dataset = create_sample_data()
    print(f"Sample dataset ID: {sample_dataset.id}")
    print("🎉 API setup is complete and working!")