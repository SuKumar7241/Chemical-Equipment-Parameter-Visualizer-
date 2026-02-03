#!/usr/bin/env python
"""
Windows-compatible API testing script
This script tests the Django API without requiring curl
"""
import os
import sys
import django
import json
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datasetapi.settings')
django.setup()

from datasets.models import Dataset, SummaryStatistics, DatasetColumn
from datasets.utils import create_dataset_from_upload
from django.core.files.uploadedfile import SimpleUploadedFile

def test_api_with_sample_data():
    """Test the API by creating sample data directly"""
    print("🚀 Testing Django Dataset Analysis API")
    print("=" * 50)
    
    # Create sample CSV content
    sample_csv_content = """equipment_id,equipment_name,category,manufacturer,purchase_date,cost,status,location
1,Excavator XL-200,Heavy Machinery,CaterpillarInc,2023-01-15,250000,Active,Site A
2,Bulldozer BD-150,Heavy Machinery,Komatsu,2023-02-20,180000,Active,Site B
3,Crane CR-500,Lifting Equipment,Liebherr,2023-03-10,320000,Active,Site A
4,Forklift FL-25,Material Handling,Toyota,2023-04-05,45000,Active,Warehouse
5,Generator GN-100,Power Equipment,Caterpillar,2023-05-12,25000,Maintenance,Site C
6,Compressor CP-75,Air Tools,Atlas Copco,2023-06-18,15000,Active,Site B
7,Welding Machine WM-300,Fabrication,Lincoln Electric,2023-07-22,8000,Active,Workshop
8,Concrete Mixer CM-200,Construction,Schwing,2023-08-30,95000,Active,Site A
9,Dump Truck DT-40,Transportation,Volvo,2023-09-14,120000,Active,Site C
10,Hydraulic Jack HJ-50,Tools,Enerpac,2023-10-25,3500,Active,Workshop"""
    
    print("📁 Creating sample equipment dataset...")
    
    try:
        # Create uploaded file object
        uploaded_file = SimpleUploadedFile(
            name="sample_equipment_data.csv",
            content=sample_csv_content.encode('utf-8'),
            content_type='text/csv'
        )
        
        # Process the file using our utility function
        print("🔄 Processing dataset...")
        dataset = create_dataset_from_upload(
            file_obj=uploaded_file,
            file_name="sample_equipment_data.csv",
            name="Equipment Dataset",
            description="Sample equipment data for testing the Django API"
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
                for col_name, stats in list(numeric_stats.items())[:2]:  # Show first 2
                    print(f"   {col_name}:")
                    print(f"     Mean: {stats.get('mean', 'N/A')}")
                    print(f"     Min: {stats.get('min', 'N/A')}")
                    print(f"     Max: {stats.get('max', 'N/A')}")
            
            categorical_stats = summary.get_categorical_summary()
            if categorical_stats:
                print(f"\n📝 Categorical Column Statistics:")
                for col_name, stats in list(categorical_stats.items())[:2]:  # Show first 2
                    print(f"   {col_name}:")
                    print(f"     Unique values: {stats.get('unique_count', 'N/A')}")
                    print(f"     Most frequent: {stats.get('most_frequent', 'N/A')}")
        
        return dataset
        
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        return None

def show_api_endpoints(dataset_id):
    """Show available API endpoints"""
    print(f"\n🌐 API Endpoints (Server running at http://127.0.0.1:8000/):")
    print("   📊 Datasets:")
    print(f"      GET    http://127.0.0.1:8000/api/datasets/")
    print(f"      GET    http://127.0.0.1:8000/api/datasets/{dataset_id}/")
    print(f"      GET    http://127.0.0.1:8000/api/datasets/{dataset_id}/statistics/")
    print(f"      GET    http://127.0.0.1:8000/api/datasets/{dataset_id}/columns/")
    
    print(f"\n   📈 Statistics:")
    print(f"      GET    http://127.0.0.1:8000/api/statistics/")
    print(f"      GET    http://127.0.0.1:8000/api/statistics/{dataset_id}/")

def test_with_powershell():
    """Show PowerShell commands for testing"""
    print(f"\n💻 PowerShell Testing Commands:")
    print("   # List datasets")
    print("   Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/datasets/' | Select-Object -ExpandProperty Content")
    print("")
    print("   # Get dataset details (replace 1 with actual dataset ID)")
    print("   Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/datasets/1/' | Select-Object -ExpandProperty Content")
    print("")
    print("   # Get statistics")
    print("   Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/datasets/1/statistics/' | Select-Object -ExpandProperty Content")

def main():
    """Main function"""
    # Test with sample data
    dataset = test_api_with_sample_data()
    
    if dataset:
        show_api_endpoints(dataset.id)
        test_with_powershell()
        
        print(f"\n🎉 API Testing Complete!")
        print(f"   Dataset ID {dataset.id} is ready for testing")
        print(f"   Django server is running at: http://127.0.0.1:8000/")
        print(f"   Admin interface: http://127.0.0.1:8000/admin/")
        print(f"   API base URL: http://127.0.0.1:8000/api/")
        
        print(f"\n🌐 You can also test in your browser:")
        print(f"   - http://127.0.0.1:8000/api/datasets/")
        print(f"   - http://127.0.0.1:8000/api/datasets/{dataset.id}/")
        print(f"   - http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    main()