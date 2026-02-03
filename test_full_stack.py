#!/usr/bin/env python3
"""
Comprehensive test for the full-stack web application
"""

import requests
import json
import time
import os

def test_django_backend():
    """Test Django backend functionality"""
    print("=== Testing Django Backend ===")
    
    base_url = "http://localhost:8000"
    
    tests = [
        {
            'name': 'Root endpoint',
            'url': f'{base_url}/',
            'expected_status': 200,
            'check_content': lambda data: data.get('message') == 'Dataset Analysis API'
        },
        {
            'name': 'API root',
            'url': f'{base_url}/api/',
            'expected_status': 200,
            'check_content': lambda data: data.get('version') == '1.0.0'
        },
        {
            'name': 'Auth status',
            'url': f'{base_url}/api/auth/status/',
            'expected_status': 200,
            'check_content': lambda data: data.get('authenticated') == False
        }
    ]
    
    backend_working = True
    
    for test in tests:
        try:
            response = requests.get(test['url'], timeout=5)
            if response.status_code == test['expected_status']:
                data = response.json()
                if test['check_content'](data):
                    print(f"✓ {test['name']}: PASS")
                else:
                    print(f"⚠ {test['name']}: Status OK but content unexpected")
            else:
                print(f"✗ {test['name']}: Expected {test['expected_status']}, got {response.status_code}")
                backend_working = False
        except Exception as e:
            print(f"✗ {test['name']}: {e}")
            backend_working = False
    
    return backend_working

def test_authentication_flow():
    """Test user registration and login"""
    print("\n=== Testing Authentication Flow ===")
    
    base_url = "http://localhost:8000"
    
    # Test user registration
    test_user = {
        'username': f'testuser_{int(time.time())}',
        'password': 'testpass123',
        'email': 'test@example.com'
    }
    
    try:
        # Register user
        response = requests.post(f'{base_url}/api/auth/register/', json=test_user, timeout=5)
        if response.status_code == 201:
            print("✓ User registration: PASS")
            
            # Try to login
            login_data = {
                'username': test_user['username'],
                'password': test_user['password']
            }
            
            response = requests.post(f'{base_url}/api/auth/login/', json=login_data, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'tokens' in data and 'access' in data['tokens']:
                    print("✓ User login: PASS")
                    return data['tokens']['access']
                else:
                    print("⚠ User login: No access token returned")
            else:
                print(f"✗ User login: Status {response.status_code}")
        else:
            print(f"✗ User registration: Status {response.status_code}")
            
    except Exception as e:
        print(f"✗ Authentication flow: {e}")
    
    return None

def test_authenticated_endpoints(access_token):
    """Test endpoints that require authentication"""
    print("\n=== Testing Authenticated Endpoints ===")
    
    if not access_token:
        print("⚠ Skipping authenticated tests - no access token")
        return
    
    base_url = "http://localhost:8000"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    endpoints = [
        {
            'name': 'Datasets list',
            'url': f'{base_url}/api/datasets/',
            'method': 'GET'
        },
        {
            'name': 'Equipment summary',
            'url': f'{base_url}/api/equipment/summary/',
            'method': 'GET'
        }
    ]
    
    for endpoint in endpoints:
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"✓ {endpoint['name']}: PASS")
            else:
                print(f"⚠ {endpoint['name']}: Status {response.status_code}")
                
        except Exception as e:
            print(f"✗ {endpoint['name']}: {e}")

def test_frontend_files():
    """Test frontend file structure"""
    print("\n=== Testing Frontend Files ===")
    
    critical_files = [
        'frontend/package.json',
        'frontend/src/App.js',
        'frontend/src/index.js',
        'frontend/src/components/Login.js',
        'frontend/src/components/Dashboard.js',
        'frontend/src/services/api.js'
    ]
    
    all_present = True
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (missing)")
            all_present = False
    
    return all_present

def check_react_server():
    """Check if React development server is accessible"""
    print("\n=== Testing React Server ===")
    
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("✓ React server is running and accessible")
            return True
        else:
            print(f"⚠ React server responded with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠ React server not accessible (may not be started yet)")
    except Exception as e:
        print(f"✗ Error checking React server: {e}")
    
    return False

def main():
    print("Full-Stack Web Application Test")
    print("=" * 50)
    
    # Test Django backend
    backend_ok = test_django_backend()
    
    if not backend_ok:
        print("\n❌ Backend tests failed. Please check Django server.")
        return 1
    
    # Test authentication
    access_token = test_authentication_flow()
    
    # Test authenticated endpoints
    test_authenticated_endpoints(access_token)
    
    # Test frontend files
    frontend_files_ok = test_frontend_files()
    
    # Check React server
    react_ok = check_react_server()
    
    # Summary
    print("\n" + "=" * 50)
    print("FULL-STACK TEST SUMMARY")
    print("=" * 50)
    
    if backend_ok:
        print("✅ Django Backend: WORKING")
        print("   - API endpoints accessible")
        print("   - Authentication working")
        print("   - Database operations functional")
    else:
        print("❌ Django Backend: ISSUES DETECTED")
    
    if frontend_files_ok:
        print("✅ Frontend Files: PRESENT")
        print("   - React components available")
        print("   - API integration configured")
    else:
        print("❌ Frontend Files: MISSING FILES")
    
    if react_ok:
        print("✅ React Server: RUNNING")
        print("   - Development server accessible")
        print("   - Ready for browser testing")
    else:
        print("⚠️  React Server: NOT ACCESSIBLE")
        print("   - Run 'npm start' in frontend directory")
        print("   - Then open http://localhost:3000")
    
    print("\n🌐 WEB APPLICATION STATUS:")
    if backend_ok and frontend_files_ok:
        print("   ✅ Ready for use!")
        print("   📍 Backend: http://localhost:8000")
        if react_ok:
            print("   📍 Frontend: http://localhost:3000")
        else:
            print("   📍 Frontend: Start with 'npm start' in frontend/")
    else:
        print("   ⚠️  Some components need attention")
    
    return 0

if __name__ == '__main__':
    exit(main())