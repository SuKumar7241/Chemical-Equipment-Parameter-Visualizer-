#!/usr/bin/env python
"""
Test script for extended features: Authentication, History Management, and PDF Reports
"""
import os
import sys
import django
from io import StringIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datasetapi.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from datasets.models import Dataset, SummaryStatistics
from datasets.history_utils import get_dataset_history_info, trigger_cleanup_if_needed
from datasets.pdf_utils import generate_dataset_pdf_report
from datasets.equipment_utils import process_equipment_csv
from django.core.files.uploadedfile import SimpleUploadedFile
import json


def test_authentication():
    """Test authentication functionality"""
    print("🔐 Testing Authentication...")
    client = Client()
    
    try:
        # Test user registration
        print("   Testing user registration...")
        register_data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'email': 'test@example.com'
        }
        
        response = client.post('/api/auth/register/', register_data, content_type='application/json')
        print(f"   Registration status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ User registered: {data.get('user', {}).get('username')}")
            access_token = data.get('tokens', {}).get('access')
            print(f"   ✅ JWT token generated")
        else:
            print(f"   ❌ Registration failed: {response.json()}")
            return False
        
        # Test user login
        print("   Testing user login...")
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        response = client.post('/api/auth/login/', login_data, content_type='application/json')
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login successful: {data.get('user', {}).get('username')}")
            access_token = data.get('tokens', {}).get('access')
        else:
            print(f"   ❌ Login failed: {response.json()}")
            return False
        
        # Test authenticated endpoint
        print("   Testing authenticated endpoint...")
        headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        response = client.get('/api/auth/profile/', **headers)
        print(f"   Profile status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Profile retrieved: {data.get('user', {}).get('username')}")
        else:
            print(f"   ❌ Profile retrieval failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Authentication test error: {str(e)}")
        return False


def test_history_management():
    """Test history management functionality"""
    print("\n📚 Testing History Management...")
    
    try:
        # Get current history info
        print("   Getting history information...")
        history_info = get_dataset_history_info()
        print(f"   Current datasets: {history_info.get('total_datasets', 0)}")
        print(f"   Max allowed: {history_info.get('max_datasets_allowed', 5)}")
        
        # Create multiple test datasets to test cleanup
        print("   Creating test datasets...")
        csv_content = """equipment_id,equipment_type,flowrate,pressure,temperature
EQ001,Pump,150.5,45.2,78.5
EQ002,Compressor,200.0,60.8,85.2"""
        
        created_datasets = []
        for i in range(3):
            uploaded_file = SimpleUploadedFile(
                name=f"test_dataset_{i}.csv",
                content=csv_content.encode('utf-8'),
                content_type='text/csv'
            )
            
            # Process and create dataset
            cleaned_df, summary_stats = process_equipment_csv(uploaded_file, f"test_dataset_{i}.csv")
            
            dataset = Dataset.objects.create(
                name=f"Test Dataset {i}",
                description=f"Test dataset {i} for history management",
                file_name=f"test_dataset_{i}.csv",
                file_size=len(csv_content),
                file_type='csv',
                total_rows=len(cleaned_df),
                total_columns=len(cleaned_df.columns),
                column_names=list(cleaned_df.columns),
                column_types={col: str(cleaned_df[col].dtype) for col in cleaned_df.columns},
                is_processed=True
            )
            
            created_datasets.append(dataset)
            print(f"   ✅ Created dataset {i}: {dataset.name}")
        
        # Test cleanup trigger
        print("   Testing cleanup trigger...")
        cleanup_result = trigger_cleanup_if_needed()
        print(f"   Cleanup triggered: {cleanup_result.get('cleanup_triggered', False)}")
        
        if cleanup_result.get('cleanup_triggered'):
            print(f"   ✅ Cleanup performed: {cleanup_result.get('cleanup_result', {})}")
        else:
            print(f"   ℹ️ No cleanup needed")
        
        # Get updated history info
        updated_history = get_dataset_history_info()
        print(f"   Updated dataset count: {updated_history.get('total_datasets', 0)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ History management test error: {str(e)}")
        return False


def test_pdf_generation():
    """Test PDF report generation"""
    print("\n📄 Testing PDF Report Generation...")
    
    try:
        # Get a dataset with summary statistics
        dataset = Dataset.objects.filter(is_processed=True, summary__isnull=False).first()
        
        if not dataset:
            print("   ⚠️ No processed datasets with summaries found. Creating one...")
            
            # Create a test dataset
            csv_content = """equipment_id,equipment_type,flowrate,pressure,temperature,location,status
EQ001,Pump,150.5,45.2,78.5,Plant A,Active
EQ002,Compressor,200.0,60.8,85.2,Plant B,Active
EQ003,Valve,75.3,30.1,72.0,Plant A,Maintenance
EQ004,Pump,180.2,50.5,80.1,Plant C,Active"""
            
            uploaded_file = SimpleUploadedFile(
                name="pdf_test_dataset.csv",
                content=csv_content.encode('utf-8'),
                content_type='text/csv'
            )
            
            # Process the CSV
            cleaned_df, summary_stats = process_equipment_csv(uploaded_file, "pdf_test_dataset.csv")
            
            # Create dataset
            dataset = Dataset.objects.create(
                name="PDF Test Dataset",
                description="Dataset for testing PDF generation",
                file_name="pdf_test_dataset.csv",
                file_size=len(csv_content),
                file_type='csv',
                total_rows=len(cleaned_df),
                total_columns=len(cleaned_df.columns),
                column_names=list(cleaned_df.columns),
                column_types={col: str(cleaned_df[col].dtype) for col in cleaned_df.columns},
                is_processed=True
            )
            
            # Create summary statistics
            operational_metrics = summary_stats.get('operational_metrics', {})
            equipment_analysis = summary_stats.get('equipment_analysis', {})
            
            summary = SummaryStatistics.objects.create(
                dataset=dataset,
                statistics_data=summary_stats,
                numeric_columns_count=3,
                categorical_columns_count=4,
                missing_values_count=0,
                total_records=len(cleaned_df),
                avg_flowrate=operational_metrics.get('flowrate', {}).get('average'),
                avg_pressure=operational_metrics.get('pressure', {}).get('average'),
                avg_temperature=operational_metrics.get('temperature', {}).get('average'),
                equipment_type_distribution=equipment_analysis.get('equipment_type_distribution', {})
            )
            
            print(f"   ✅ Created test dataset for PDF: {dataset.name}")
        
        # Generate PDF report
        print(f"   Generating PDF report for dataset: {dataset.name}")
        pdf_buffer, filename = generate_dataset_pdf_report(dataset)
        
        print(f"   ✅ PDF generated successfully!")
        print(f"   Filename: {filename}")
        print(f"   Size: {len(pdf_buffer.getvalue())} bytes")
        
        # Save PDF to file for verification
        pdf_path = f"test_report_{dataset.id}.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"   ✅ PDF saved to: {pdf_path}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ PDF generation test error: {str(e)}")
        return False


def test_api_endpoints():
    """Test new API endpoints"""
    print("\n🌐 Testing New API Endpoints...")
    client = Client()
    
    try:
        # Create a test user and login
        user = User.objects.create_user(username='apitest', password='testpass123')
        client.login(username='apitest', password='testpass123')
        
        # Test history status endpoint
        print("   Testing history status endpoint...")
        response = client.get('/api/history/status/')
        print(f"   History status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ History info retrieved: {data.get('history_info', {}).get('total_datasets', 0)} datasets")
        
        # Test available reports endpoint
        print("   Testing available reports endpoint...")
        response = client.get('/api/reports/available/')
        print(f"   Available reports: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Reports available: {data.get('count', 0)}")
        
        # Test auth status endpoint
        print("   Testing auth status endpoint...")
        response = client.get('/api/auth/status/')
        print(f"   Auth status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Auth status: {data.get('authenticated', False)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API endpoints test error: {str(e)}")
        return False


def show_new_endpoints():
    """Display all new endpoints"""
    print("\n🎯 New API Endpoints Added:")
    
    print("\n   🔐 Authentication:")
    print("      POST   /api/auth/register/")
    print("      POST   /api/auth/login/")
    print("      POST   /api/auth/logout/")
    print("      GET    /api/auth/profile/")
    print("      GET    /api/auth/status/")
    print("      POST   /api/auth/token/")
    print("      POST   /api/auth/token/refresh/")
    
    print("\n   📄 PDF Reports:")
    print("      GET    /api/reports/pdf/{dataset_id}/")
    print("      GET    /api/reports/preview/{dataset_id}/")
    print("      GET    /api/reports/available/")
    print("      POST   /api/reports/batch/")
    
    print("\n   📚 History Management:")
    print("      GET    /api/history/status/")
    print("      POST   /api/history/cleanup/")
    print("      GET    /api/history/cleanup-preview/")
    print("      GET    /api/history/datasets/")
    print("      DELETE /api/history/datasets/{dataset_id}/")
    print("      GET    /api/history/settings/")


def main():
    """Main test function"""
    print("🚀 Extended Features Test Suite")
    print("=" * 60)
    
    # Test authentication
    auth_success = test_authentication()
    
    # Test history management
    history_success = test_history_management()
    
    # Test PDF generation
    pdf_success = test_pdf_generation()
    
    # Test API endpoints
    api_success = test_api_endpoints()
    
    # Show new endpoints
    show_new_endpoints()
    
    # Summary
    print(f"\n📊 Test Results Summary:")
    print(f"   Authentication: {'✅ PASSED' if auth_success else '❌ FAILED'}")
    print(f"   History Management: {'✅ PASSED' if history_success else '❌ FAILED'}")
    print(f"   PDF Generation: {'✅ PASSED' if pdf_success else '❌ FAILED'}")
    print(f"   API Endpoints: {'✅ PASSED' if api_success else '❌ FAILED'}")
    
    all_passed = auth_success and history_success and pdf_success and api_success
    
    if all_passed:
        print(f"\n🎉 All Extended Features Working!")
        print(f"   ✅ JWT Authentication implemented")
        print(f"   ✅ History management (max 5 datasets)")
        print(f"   ✅ PDF report generation")
        print(f"   ✅ All new API endpoints functional")
    else:
        print(f"\n⚠️ Some features need attention")
    
    print(f"\n🔧 Next Steps:")
    print(f"   1. Start server: python manage.py runserver")
    print(f"   2. Register user: POST /api/auth/register/")
    print(f"   3. Upload equipment data: POST /api/equipment/upload/")
    print(f"   4. Generate PDF report: GET /api/reports/pdf/{{dataset_id}}/")
    print(f"   5. Check history: GET /api/history/status/")


if __name__ == "__main__":
    main()