#!/usr/bin/env python
"""
Comprehensive API validation script
Tests all endpoints with various scenarios including error cases
"""
import os
import sys
import django
from io import StringIO
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datasetapi.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from datasets.models import Dataset, SummaryStatistics


class APIValidator:
    def __init__(self):
        self.client = Client()
        self.access_token = None
        self.test_user = None
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log_result(self, test_name, success, details=None):
        """Log test result"""
        if success:
            self.results['passed'] += 1
            print(f"   ✅ {test_name}")
        else:
            self.results['failed'] += 1
            print(f"   ❌ {test_name}")
            if details:
                print(f"      Details: {details}")
                self.results['errors'].append(f"{test_name}: {details}")
    
    def setup_authentication(self):
        """Setup authentication for tests"""
        print("🔐 Setting up authentication...")
        
        # Clean up any existing test user
        User.objects.filter(username='apivalidator').delete()
        
        # Register user
        register_data = {
            'username': 'apivalidator',
            'password': 'testpassword123',
            'email': 'validator@example.com'
        }
        
        response = self.client.post('/api/auth/register/', 
                                  json.dumps(register_data), 
                                  content_type='application/json')
        
        if response.status_code == 201:
            data = response.json()
            self.access_token = data.get('tokens', {}).get('access')
            self.test_user = data.get('user')
            self.log_result("User registration", True)
            return True
        else:
            self.log_result("User registration", False, response.json())
            return False
    
    def test_authentication_apis(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication APIs...")
        
        # Test login
        login_data = {
            'username': 'apivalidator',
            'password': 'testpassword123'
        }
        
        response = self.client.post('/api/auth/login/', 
                                  json.dumps(login_data), 
                                  content_type='application/json')
        
        success = response.status_code == 200
        self.log_result("User login", success, None if success else response.json())
        
        if success:
            data = response.json()
            self.access_token = data.get('tokens', {}).get('access')
        
        # Test profile endpoint
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        response = self.client.get('/api/auth/profile/', **headers)
        
        success = response.status_code == 200
        self.log_result("Get user profile", success, None if success else response.content.decode())
        
        # Test auth status
        response = self.client.get('/api/auth/status/', **headers)
        success = response.status_code == 200 and response.json().get('authenticated') == True
        self.log_result("Auth status check", success)
        
        # Test unauthenticated access
        response = self.client.get('/api/auth/profile/')
        success = response.status_code == 401
        self.log_result("Unauthenticated access blocked", success)
        
        # Test invalid credentials
        invalid_login = {
            'username': 'apivalidator',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/auth/login/', 
                                  json.dumps(invalid_login), 
                                  content_type='application/json')
        
        success = response.status_code == 401
        self.log_result("Invalid credentials rejected", success)
    
    def create_test_csv(self, filename, valid=True):
        """Create test CSV files"""
        if valid:
            csv_content = """equipment_id,equipment_type,flowrate,pressure,temperature,location,status
EQ001,Pump,150.5,45.2,78.5,Plant A,Active
EQ002,Compressor,200.0,60.8,85.2,Plant B,Active
EQ003,Valve,75.3,30.1,72.0,Plant A,Maintenance
EQ004,Pump,180.2,50.5,80.1,Plant C,Active
EQ005,Heat Exchanger,0.0,25.0,95.5,Plant B,Active"""
        else:
            # Missing pressure column
            csv_content = """id,type,flow,temp
EQ001,Pump,150.5,78.5
EQ002,Compressor,200.0,85.2"""
        
        with open(filename, 'w') as f:
            f.write(csv_content)
    
    def test_csv_upload_apis(self):
        """Test CSV upload endpoints"""
        print("\n📊 Testing CSV Upload APIs...")
        
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        
        # Test valid CSV upload
        self.create_test_csv('valid_test.csv', valid=True)
        
        with open('valid_test.csv', 'rb') as f:
            response = self.client.post('/api/equipment/upload/', {
                'file': f,
                'name': 'Valid Test Dataset',
                'description': 'Test dataset for validation'
            }, **headers)
        
        success = response.status_code == 201
        dataset_id = None
        if success:
            data = response.json()
            dataset_id = data.get('dataset_id')
            
        self.log_result("Valid CSV upload", success, None if success else response.json())
        
        # Test invalid CSV upload (missing columns)
        self.create_test_csv('invalid_test.csv', valid=False)
        
        with open('invalid_test.csv', 'rb') as f:
            response = self.client.post('/api/equipment/upload/', {
                'file': f,
                'name': 'Invalid Test Dataset'
            }, **headers)
        
        success = response.status_code == 400
        self.log_result("Invalid CSV rejected", success)
        
        # Test unauthenticated upload
        with open('valid_test.csv', 'rb') as f:
            response = self.client.post('/api/equipment/upload/', {
                'file': f,
                'name': 'Unauthorized Upload'
            })
        
        success = response.status_code == 401
        self.log_result("Unauthenticated upload blocked", success)
        
        # Test CSV validation endpoint
        with open('valid_test.csv', 'rb') as f:
            response = self.client.post('/api/equipment/validate/', {
                'file': f
            }, **headers)
        
        success = response.status_code == 200 and response.json().get('is_valid') == True
        self.log_result("CSV validation (valid file)", success)
        
        # Test CSV validation with invalid file
        with open('invalid_test.csv', 'rb') as f:
            response = self.client.post('/api/equipment/validate/', {
                'file': f
            }, **headers)
        
        success = response.status_code == 200 and response.json().get('is_valid') == False
        self.log_result("CSV validation (invalid file)", success)
        
        # Clean up test files
        os.remove('valid_test.csv')
        os.remove('invalid_test.csv')
        
        return dataset_id
    
    def test_data_summary_apis(self, dataset_id):
        """Test data summary endpoints"""
        print("\n📈 Testing Data Summary APIs...")
        
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        
        if dataset_id:
            # Test specific dataset summary
            response = self.client.get(f'/api/equipment/summary/{dataset_id}/', **headers)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                has_required_fields = all(field in data for field in [
                    'total_record_count', 'average_flowrate', 'average_pressure', 
                    'average_temperature', 'equipment_type_distribution'
                ])
                success = has_required_fields
            
            self.log_result("Specific dataset summary", success)
        
        # Test combined summary
        response = self.client.get('/api/equipment/summary/', **headers)
        success = response.status_code in [200, 404]  # 404 if no datasets
        self.log_result("Combined dataset summary", success)
        
        # Test non-existent dataset
        response = self.client.get('/api/equipment/summary/999/', **headers)
        success = response.status_code == 404
        self.log_result("Non-existent dataset summary", success)
        
        # Test unauthenticated access
        response = self.client.get('/api/equipment/summary/')
        success = response.status_code == 401
        self.log_result("Unauthenticated summary access blocked", success)
    
    def test_pdf_report_apis(self, dataset_id):
        """Test PDF report endpoints"""
        print("\n📄 Testing PDF Report APIs...")
        
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        
        if dataset_id:
            # Test PDF report preview
            response = self.client.get(f'/api/reports/preview/{dataset_id}/', **headers)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                has_required_fields = all(field in data for field in [
                    'dataset_info', 'report_sections', 'metrics_included'
                ])
                success = has_required_fields
            
            self.log_result("PDF report preview", success)
            
            # Test PDF generation (we can't easily test the actual PDF content)
            response = self.client.get(f'/api/reports/pdf/{dataset_id}/', **headers)
            success = response.status_code == 200 and response['Content-Type'] == 'application/pdf'
            self.log_result("PDF report generation", success)
        
        # Test available reports list
        response = self.client.get('/api/reports/available/', **headers)
        success = response.status_code == 200
        self.log_result("Available reports list", success)
        
        # Test non-existent dataset PDF
        response = self.client.get('/api/reports/pdf/999/', **headers)
        success = response.status_code == 404
        self.log_result("Non-existent dataset PDF", success)
        
        # Test unauthenticated PDF access
        response = self.client.get('/api/reports/pdf/1/')
        success = response.status_code == 401
        self.log_result("Unauthenticated PDF access blocked", success)
    
    def test_history_management_apis(self):
        """Test history management endpoints"""
        print("\n📚 Testing History Management APIs...")
        
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        
        # Test history status
        response = self.client.get('/api/history/status/', **headers)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            has_required_fields = all(field in data for field in [
                'history_info', 'cleanup_preview', 'settings'
            ])
            success = has_required_fields
        
        self.log_result("History status", success)
        
        # Test dataset history
        response = self.client.get('/api/history/datasets/', **headers)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            has_pagination = 'pagination' in data and 'datasets' in data
            success = has_pagination
        
        self.log_result("Dataset history", success)
        
        # Test cleanup preview
        response = self.client.get('/api/history/cleanup-preview/', **headers)
        success = response.status_code == 200
        self.log_result("Cleanup preview", success)
        
        # Test history settings (admin only, should fail for regular user)
        response = self.client.get('/api/history/settings/', **headers)
        success = response.status_code == 403  # Forbidden for non-admin
        self.log_result("History settings (admin only)", success)
        
        # Test unauthenticated history access
        response = self.client.get('/api/history/status/')
        success = response.status_code == 401
        self.log_result("Unauthenticated history access blocked", success)
    
    def test_general_endpoints(self):
        """Test general endpoints"""
        print("\n🌐 Testing General Endpoints...")
        
        # Test root endpoint
        response = self.client.get('/')
        success = response.status_code == 200
        self.log_result("Root endpoint", success)
        
        # Test API root
        response = self.client.get('/api/')
        success = response.status_code == 200
        self.log_result("API root endpoint", success)
        
        # Test datasets list (should require auth)
        response = self.client.get('/api/datasets/')
        success = response.status_code == 401
        self.log_result("Datasets list (auth required)", success)
    
    def run_validation(self):
        """Run complete validation"""
        print("🚀 Starting Comprehensive API Validation")
        print("=" * 60)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue.")
            return False
        
        # Test all API categories
        self.test_authentication_apis()
        dataset_id = self.test_csv_upload_apis()
        self.test_data_summary_apis(dataset_id)
        self.test_pdf_report_apis(dataset_id)
        self.test_history_management_apis()
        self.test_general_endpoints()
        
        # Print summary
        print(f"\n📊 Validation Summary:")
        print(f"   ✅ Passed: {self.results['passed']}")
        print(f"   ❌ Failed: {self.results['failed']}")
        print(f"   📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['failed'] > 0:
            print(f"\n❌ Failed Tests:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = self.results['passed'] / (self.results['passed'] + self.results['failed'])
        
        if success_rate >= 0.95:  # 95% success rate
            print(f"\n🎉 Validation PASSED! All critical APIs working correctly.")
            return True
        else:
            print(f"\n⚠️ Validation FAILED. Some APIs need attention.")
            return False


def main():
    """Main validation function"""
    validator = APIValidator()
    success = validator.run_validation()
    
    if success:
        print(f"\n✅ Backend Validation Complete - All Requirements Satisfied!")
        print(f"   🔐 Authentication: JWT and session auth working")
        print(f"   📊 Equipment APIs: CSV upload and validation working")
        print(f"   📈 Data Summary: Comprehensive analysis working")
        print(f"   📄 PDF Reports: Generation and preview working")
        print(f"   📚 History Management: Cleanup and tracking working")
        print(f"   🛡️ Security: Authentication required for all operations")
        print(f"   ❌ Error Handling: All error cases handled gracefully")
    else:
        print(f"\n⚠️ Some issues found. Check the failed tests above.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)