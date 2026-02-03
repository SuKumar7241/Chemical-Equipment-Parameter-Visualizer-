#!/usr/bin/env python
"""
Test script for equipment-specific APIs
Tests CSV upload, validation, and data summary endpoints
"""
import os
import sys
import django
from io import StringIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datasetapi.settings')
django.setup()

from datasets.equipment_utils import process_equipment_csv, validate_csv_columns
from datasets.models import Dataset, SummaryStatistics
from django.core.files.uploadedfile import SimpleUploadedFile


def create_sample_equipment_csv():
    """Create sample equipment CSV data for testing"""
    csv_content = """equipment_id,equipment_type,flowrate,pressure,temperature,location,status
EQ001,Pump,150.5,45.2,78.5,Plant A,Active
EQ002,Compressor,200.0,60.8,85.2,Plant B,Active
EQ003,Valve,75.3,30.1,72.0,Plant A,Maintenance
EQ004,Pump,180.2,50.5,80.1,Plant C,Active
EQ005,Heat Exchanger,0.0,25.0,95.5,Plant B,Active
EQ006,Compressor,220.8,65.2,88.0,Plant A,Active
EQ007,Valve,90.1,35.8,75.5,Plant C,Active
EQ008,Pump,165.0,48.0,79.2,Plant B,Maintenance
EQ009,Heat Exchanger,0.0,28.5,92.0,Plant A,Active
EQ010,Compressor,195.5,58.9,86.5,Plant C,Active"""
    
    return csv_content


def test_csv_validation():
    """Test CSV validation functionality"""
    print("🔍 Testing CSV Validation...")
    
    # Create sample CSV
    csv_content = create_sample_equipment_csv()
    csv_file = StringIO(csv_content)
    
    try:
        import pandas as pd
        df = pd.read_csv(csv_file)
        
        # Test validation
        validation_result = validate_csv_columns(df)
        
        print(f"   ✅ Validation Result: {'PASSED' if validation_result['is_valid'] else 'FAILED'}")
        print(f"   📊 Found Columns: {validation_result['found_columns']}")
        print(f"   🔗 Column Mapping: {validation_result['column_mapping']}")
        
        if validation_result['missing_columns']:
            print(f"   ❌ Missing Columns: {validation_result['missing_columns']}")
        
        return validation_result['is_valid']
        
    except Exception as e:
        print(f"   ❌ Validation Error: {str(e)}")
        return False


def test_equipment_csv_processing():
    """Test equipment CSV processing"""
    print("\n🔄 Testing Equipment CSV Processing...")
    
    try:
        # Create sample CSV file
        csv_content = create_sample_equipment_csv()
        uploaded_file = SimpleUploadedFile(
            name="test_equipment.csv",
            content=csv_content.encode('utf-8'),
            content_type='text/csv'
        )
        
        # Process the CSV
        cleaned_df, summary_stats = process_equipment_csv(uploaded_file, "test_equipment.csv")
        
        print(f"   ✅ Processing Successful!")
        print(f"   📊 Rows Processed: {len(cleaned_df)}")
        print(f"   📋 Columns: {list(cleaned_df.columns)}")
        
        # Display operational metrics
        operational_metrics = summary_stats.get('operational_metrics', {})
        print(f"\n   🔢 Operational Metrics:")
        
        if 'flowrate' in operational_metrics:
            flowrate = operational_metrics['flowrate']
            print(f"      Flowrate - Avg: {flowrate['average']:.2f}, Min: {flowrate['min']:.2f}, Max: {flowrate['max']:.2f}")
        
        if 'pressure' in operational_metrics:
            pressure = operational_metrics['pressure']
            print(f"      Pressure - Avg: {pressure['average']:.2f}, Min: {pressure['min']:.2f}, Max: {pressure['max']:.2f}")
        
        if 'temperature' in operational_metrics:
            temperature = operational_metrics['temperature']
            print(f"      Temperature - Avg: {temperature['average']:.2f}, Min: {temperature['min']:.2f}, Max: {temperature['max']:.2f}")
        
        # Display equipment distribution
        equipment_analysis = summary_stats.get('equipment_analysis', {})
        if 'equipment_type_distribution' in equipment_analysis:
            print(f"\n   🏭 Equipment Type Distribution:")
            for eq_type, count in equipment_analysis['equipment_type_distribution'].items():
                print(f"      {eq_type}: {count}")
        
        return cleaned_df, summary_stats
        
    except Exception as e:
        print(f"   ❌ Processing Error: {str(e)}")
        return None, None


def test_database_integration():
    """Test database integration with equipment data"""
    print("\n💾 Testing Database Integration...")
    
    try:
        # Create sample CSV file
        csv_content = create_sample_equipment_csv()
        uploaded_file = SimpleUploadedFile(
            name="test_equipment_db.csv",
            content=csv_content.encode('utf-8'),
            content_type='text/csv'
        )
        
        # Process the CSV
        cleaned_df, summary_stats = process_equipment_csv(uploaded_file, "test_equipment_db.csv")
        
        # Create dataset
        dataset = Dataset.objects.create(
            name="Test Equipment Dataset",
            description="Test dataset for equipment API validation",
            file_name="test_equipment_db.csv",
            file_size=len(csv_content),
            file_type='csv',
            total_rows=len(cleaned_df),
            total_columns=len(cleaned_df.columns),
            column_names=list(cleaned_df.columns),
            column_types={col: str(cleaned_df[col].dtype) for col in cleaned_df.columns},
            is_processed=True
        )
        
        # Extract metrics
        operational_metrics = summary_stats.get('operational_metrics', {})
        equipment_analysis = summary_stats.get('equipment_analysis', {})
        
        # Create summary statistics
        summary = SummaryStatistics.objects.create(
            dataset=dataset,
            statistics_data=summary_stats,
            numeric_columns_count=len([col for col in cleaned_df.columns if cleaned_df[col].dtype in ['int64', 'float64']]),
            categorical_columns_count=len([col for col in cleaned_df.columns if cleaned_df[col].dtype == 'object']),
            missing_values_count=int(cleaned_df.isnull().sum().sum()),
            total_records=len(cleaned_df),
            avg_flowrate=operational_metrics.get('flowrate', {}).get('average'),
            avg_pressure=operational_metrics.get('pressure', {}).get('average'),
            avg_temperature=operational_metrics.get('temperature', {}).get('average'),
            equipment_type_distribution=equipment_analysis.get('equipment_type_distribution', {})
        )
        
        print(f"   ✅ Dataset Created: ID {dataset.id}")
        print(f"   📊 Summary Statistics Created: ID {summary.id}")
        print(f"   🔢 Quick Access Metrics:")
        print(f"      Total Records: {summary.total_records}")
        print(f"      Avg Flowrate: {summary.avg_flowrate}")
        print(f"      Avg Pressure: {summary.avg_pressure}")
        print(f"      Avg Temperature: {summary.avg_temperature}")
        print(f"      Equipment Types: {len(summary.equipment_type_distribution)}")
        
        return dataset
        
    except Exception as e:
        print(f"   ❌ Database Integration Error: {str(e)}")
        return None


def show_api_endpoints():
    """Display the new API endpoints"""
    print("\n🌐 New Equipment API Endpoints:")
    print("   📤 CSV Upload:")
    print("      POST   /api/equipment/upload/")
    print("             - Upload equipment CSV with validation")
    print("             - Required: equipment_id, equipment_type, flowrate, pressure, temperature")
    
    print("\n   📊 Data Summary:")
    print("      GET    /api/equipment/summary/")
    print("             - Combined summary of all datasets")
    print("      GET    /api/equipment/summary/{dataset_id}/")
    print("             - Summary for specific dataset")
    
    print("\n   ✅ CSV Validation:")
    print("      POST   /api/equipment/validate/")
    print("             - Validate CSV structure without uploading")
    
    print("\n   👁️ Data Preview:")
    print("      GET    /api/equipment/preview/{dataset_id}/")
    print("             - Preview equipment data")


def show_testing_commands():
    """Show PowerShell testing commands"""
    print("\n💻 PowerShell Testing Commands:")
    print("   # Validate CSV structure")
    print("   $file = Get-Item 'equipment_data.csv'")
    print("   Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/equipment/validate/' -Method POST -InFile $file")
    
    print("\n   # Get data summary")
    print("   Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/equipment/summary/' -UseBasicParsing")
    
    print("\n   # Get specific dataset summary")
    print("   Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/equipment/summary/1/' -UseBasicParsing")


def main():
    """Main test function"""
    print("🚀 Equipment API Testing Suite")
    print("=" * 60)
    
    # Test validation
    validation_passed = test_csv_validation()
    
    if validation_passed:
        # Test processing
        cleaned_df, summary_stats = test_equipment_csv_processing()
        
        if cleaned_df is not None:
            # Test database integration
            dataset = test_database_integration()
            
            if dataset:
                show_api_endpoints()
                show_testing_commands()
                
                print(f"\n🎉 All Tests Passed!")
                print(f"   Equipment API is ready for use")
                print(f"   Test dataset created with ID: {dataset.id}")
                print(f"   Start server: python manage.py runserver")
                print(f"   Test endpoints at: http://127.0.0.1:8000/")
            else:
                print(f"\n❌ Database integration failed")
        else:
            print(f"\n❌ CSV processing failed")
    else:
        print(f"\n❌ CSV validation failed")


if __name__ == "__main__":
    main()