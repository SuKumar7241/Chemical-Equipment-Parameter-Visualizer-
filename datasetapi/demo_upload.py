#!/usr/bin/env python
"""
Demo script to test dataset upload functionality
This script demonstrates how to upload and analyze the sample_equipment_data.csv file
"""
import os
import sys
import django
import requests
import json
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datasetapi.settings')
django.setup()

from datasets.models import Dataset, SummaryStatistics, DatasetColumn
from datasets.utils import create_dataset_from_upload
from django.core.files.uploadedfile import SimpleUploadedFile

def test_with_sample_file(file_path):
    """Test the API with a sample CSV file"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        print("Please download the sample_equipment_data.csv file and place it in the datasetapi directory")
        return
    
    print(f"📁 Testing with file: {file_path}")
    
    try:
        # Read the file
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Create uploaded file object
        uploaded_file = SimpleUploadedFile(
            name=os.path.basename(file_path),
            content=file_content,
            content_type='text/csv'
        )
        
        # Process the file using our utility function
        print("🔄 Processing dataset...")
        dataset = create_dataset_from_upload(
            file_obj=uploaded_file,
            file_name=os.path.basename(file_path),
            name="Sample Equipment Data",
            description="Equipment dataset for demonstration purposes"
        )
        
        print(f"✅ Dataset created successfully!")
        print(f"   ID: {dataset.id}")
        print(f"   Name: {dataset.name}")
        print(f"   Rows: {dataset.total_rows}")
        print(f"   Columns: {dataset.total_columns}")
        print(f"   File Type: {dataset.file_type}")
        print(f"   Processed: {dataset.is_processed}")
        
        # Display column information
        print(f"\n📊 Column Information:")
        for i, col_name in enumerate(dataset.column_names):
            col_type = dataset.column_types.get(col_name, 'unknown')
            print(f"   {i+1}. {col_name} ({col_type})")
        
        # Display statistics if available
        if hasattr(dataset, 'summary'):
            summary = dataset.summary
            print(f"\n📈 Statistics Summary:")
            print(f"   Numeric columns: {summary.numeric_columns_count}")
            print(f"   Categorical columns: {summary.categorical_columns_count}")
            print(f"   Missing values: {summary.missing_values_count}")
            
            # Show some detailed statistics
            numeric_stats = summary.get_numeric_summary()
            if numeric_stats:
                print(f"\n🔢 Numeric Column Statistics:")
                for col_name, stats in list(numeric_stats.items())[:3]:  # Show first 3
                    print(f"   {col_name}:")
                    print(f"     Mean: {stats.get('mean', 'N/A')}")
                    print(f"     Min: {stats.get('min', 'N/A')}")
                    print(f"     Max: {stats.get('max', 'N/A')}")
            
            categorical_stats = summary.get_categorical_summary()
            if categorical_stats:
                print(f"\n📝 Categorical Column Statistics:")
                for col_name, stats in list(categorical_stats.items())[:3]:  # Show first 3
                    print(f"   {col_name}:")
                    print(f"     Unique values: {stats.get('unique_count', 'N/A')}")
                    print(f"     Most frequent: {stats.get('most_frequent', 'N/A')}")
        
        return dataset
        
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        return None

def test_api_endpoints(dataset_id):
    """Test API endpoints with the uploaded dataset"""
    base_url = "http://localhost:8000/api"
    
    print(f"\n🌐 Testing API Endpoints:")
    print("   (Note: Start the Django server with 'python manage.py runserver' to test these)")
    
    endpoints = [
        f"{base_url}/datasets/",
        f"{base_url}/datasets/{dataset_id}/",
        f"{base_url}/datasets/{dataset_id}/statistics/",
        f"{base_url}/datasets/{dataset_id}/columns/",
    ]
    
    for endpoint in endpoints:
        print(f"   📡 {endpoint}")

def main():
    """Main demo function"""
    print("🚀 Django Dataset Analysis API Demo")
    print("=" * 50)
    
    # Look for the sample equipment data file
    possible_files = [
        "sample_equipment_data.csv",
        "../sample_equipment_data.csv",
        "sample_data.csv"  # fallback to our created sample
    ]
    
    file_to_use = None
    for file_path in possible_files:
        if os.path.exists(file_path):
            file_to_use = file_path
            break
    
    if not file_to_use:
        print("📥 Sample files not found. Please:")
        print("   1. Download sample_equipment_data.csv from the Google Drive link")
        print("   2. Place it in the datasetapi directory")
        print("   3. Run this script again")
        print("\n   Alternative: The script will work with any CSV file you place here.")
        return
    
    # Test with the sample file
    dataset = test_with_sample_file(file_to_use)
    
    if dataset:
        test_api_endpoints(dataset.id)
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"   Dataset ID {dataset.id} is ready for API testing")
        print(f"   Start the server: python manage.py runserver")
        print(f"   Then visit: http://localhost:8000/admin/ to see the data")

if __name__ == "__main__":
    main()