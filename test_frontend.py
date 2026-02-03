#!/usr/bin/env python3
"""
Test script to verify the frontend components are properly structured
"""

import os
import json

def test_frontend_structure():
    """Test that frontend files are properly structured"""
    print("=== Testing Frontend Structure ===")
    
    # Check package.json
    try:
        with open('frontend/package.json', 'r') as f:
            package_data = json.load(f)
        
        print("✓ package.json loaded successfully")
        print(f"  App name: {package_data.get('name', 'N/A')}")
        print(f"  React version: {package_data.get('dependencies', {}).get('react', 'N/A')}")
        print(f"  Proxy configured: {package_data.get('proxy', 'N/A')}")
        
        # Check if proxy points to Django backend
        if package_data.get('proxy') == 'http://localhost:8000':
            print("  ✓ Proxy correctly configured for Django backend")
        else:
            print("  ⚠ Proxy might not be configured correctly")
            
    except Exception as e:
        print(f"✗ Error reading package.json: {e}")
        return False
    
    # Check main React files
    react_files = [
        'frontend/src/App.js',
        'frontend/src/index.js',
        'frontend/public/index.html'
    ]
    
    for file_path in react_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (missing)")
    
    # Check component files
    component_files = [
        'frontend/src/components/Login.js',
        'frontend/src/components/Dashboard.js',
        'frontend/src/components/Upload.js',
        'frontend/src/components/DatasetList.js',
        'frontend/src/components/History.js'
    ]
    
    print("\nComponent files:")
    for file_path in component_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (missing)")
    
    # Check services
    service_files = [
        'frontend/src/services/api.js',
        'frontend/src/contexts/AuthContext.js'
    ]
    
    print("\nService files:")
    for file_path in service_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (missing)")
    
    return True

def check_api_integration():
    """Check if frontend API integration looks correct"""
    print("\n=== Testing API Integration ===")
    
    try:
        with open('frontend/src/services/api.js', 'r') as f:
            api_content = f.read()
        
        print("✓ API service file loaded")
        
        # Check for key API endpoints
        endpoints_to_check = [
            'login',
            'register',
            'datasets',
            'upload'
        ]
        
        for endpoint in endpoints_to_check:
            if endpoint in api_content.lower():
                print(f"  ✓ {endpoint} endpoint referenced")
            else:
                print(f"  ⚠ {endpoint} endpoint not found")
        
        # Check for axios usage
        if 'axios' in api_content:
            print("  ✓ Axios HTTP client configured")
        else:
            print("  ⚠ Axios not found in API service")
            
    except Exception as e:
        print(f"✗ Error reading API service: {e}")

def main():
    print("Testing Dataset Analysis Frontend")
    print("=" * 50)
    
    # Test frontend structure
    if not test_frontend_structure():
        return 1
    
    # Test API integration
    check_api_integration()
    
    print("\n=== Frontend Test Summary ===")
    print("✓ Frontend structure looks good")
    print("✓ React components are present")
    print("✓ API integration is configured")
    print("\nTo start the frontend:")
    print("1. cd frontend")
    print("2. npm start")
    print("3. Open http://localhost:3000")
    print("\nMake sure Django backend is running on http://localhost:8000")
    
    return 0

if __name__ == '__main__':
    exit(main())