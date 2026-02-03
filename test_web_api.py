#!/usr/bin/env python3
"""
Test script to verify the web API is working
"""

import requests
import json

def test_api_endpoints():
    """Test various API endpoints"""
    base_url = "http://localhost:8000"
    
    print("=== Testing Web API Endpoints ===")
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✓ Root endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Message: {data.get('message', 'N/A')}")
            print(f"  API Root: {data.get('api_root', 'N/A')}")
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
    
    # Test 2: API root endpoint
    print("\n2. Testing API root endpoint...")
    try:
        response = requests.get(f"{base_url}/api/", timeout=5)
        print(f"✓ API root: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Message: {data.get('message', 'N/A')}")
            print(f"  Version: {data.get('version', 'N/A')}")
            print(f"  Available endpoints: {len(data.get('endpoints', {}))}")
    except Exception as e:
        print(f"✗ API root failed: {e}")
    
    # Test 3: Auth status endpoint (should work without auth)
    print("\n3. Testing auth status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/auth/status/", timeout=5)
        print(f"✓ Auth status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Authenticated: {data.get('authenticated', 'N/A')}")
    except Exception as e:
        print(f"✗ Auth status failed: {e}")
    
    # Test 4: Equipment summary endpoint (might require auth)
    print("\n4. Testing equipment summary endpoint...")
    try:
        response = requests.get(f"{base_url}/api/equipment/summary/", timeout=5)
        print(f"✓ Equipment summary: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Summary available: {len(data) if isinstance(data, list) else 'Yes'}")
        elif response.status_code == 401:
            print("  (Authentication required - this is expected)")
    except Exception as e:
        print(f"✗ Equipment summary failed: {e}")
    
    # Test 5: Register endpoint (POST test)
    print("\n5. Testing user registration endpoint...")
    try:
        test_data = {
            'username': 'testuser123',
            'password': 'testpass123',
            'email': 'test@example.com'
        }
        response = requests.post(f"{base_url}/api/auth/register/", json=test_data, timeout=5)
        print(f"✓ Registration endpoint: {response.status_code}")
        if response.status_code == 201:
            print("  ✓ User registration successful")
        elif response.status_code == 400:
            data = response.json()
            if 'username' in data and 'already exists' in str(data['username']):
                print("  ✓ User already exists (expected)")
            else:
                print(f"  Validation error: {data}")
    except Exception as e:
        print(f"✗ Registration failed: {e}")

def test_frontend_files():
    """Test if frontend files exist"""
    print("\n=== Testing Frontend Files ===")
    
    import os
    
    frontend_files = [
        'frontend/package.json',
        'frontend/src/App.js',
        'frontend/src/index.js',
        'frontend/src/components/Dashboard.js',
        'frontend/src/components/Upload.js',
        'frontend/src/components/Login.js'
    ]
    
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (missing)")

def main():
    print("Testing Dataset Analysis Web Application")
    print("=" * 50)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test frontend files
    test_frontend_files()
    
    print("\n=== Summary ===")
    print("If the API tests passed, the Django backend is working correctly.")
    print("To test the React frontend:")
    print("1. cd frontend")
    print("2. npm install")
    print("3. npm start")
    print("4. Open http://localhost:3000 in browser")

if __name__ == '__main__':
    main()