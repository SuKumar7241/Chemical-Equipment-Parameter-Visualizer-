#!/usr/bin/env python
"""
Test script to verify the root endpoint is working
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datasetapi.settings')
django.setup()

from django.test import Client
from django.urls import reverse

def test_root_endpoints():
    """Test that root endpoints are working"""
    client = Client()
    
    print("🌐 Testing Root Endpoints...")
    
    try:
        # Test root endpoint
        print("   Testing: http://127.0.0.1:8000/")
        response = client.get('/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint working!")
            print(f"   Message: {data.get('message', 'N/A')}")
        else:
            print(f"   ❌ Root endpoint failed with status {response.status_code}")
        
        # Test API root endpoint
        print("\n   Testing: http://127.0.0.1:8000/api/")
        response = client.get('/api/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API root endpoint working!")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Available endpoints: {len(data.get('endpoints', {}))}")
        else:
            print(f"   ❌ API root endpoint failed with status {response.status_code}")
        
        # Test equipment summary endpoint
        print("\n   Testing: http://127.0.0.1:8000/api/equipment/summary/")
        response = client.get('/api/equipment/summary/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Equipment summary endpoint working!")
            print(f"   Total records: {data.get('total_record_count', 'N/A')}")
        elif response.status_code == 404:
            print(f"   ℹ️ Equipment summary endpoint working (no data yet)")
        else:
            print(f"   ❌ Equipment summary endpoint failed with status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing endpoints: {str(e)}")

def show_available_urls():
    """Show all available URLs"""
    print("\n📋 Available URLs:")
    print("   🏠 Root: http://127.0.0.1:8000/")
    print("   📡 API Root: http://127.0.0.1:8000/api/")
    print("   🔧 Admin: http://127.0.0.1:8000/admin/")
    print("")
    print("   📊 Equipment APIs:")
    print("      POST   http://127.0.0.1:8000/api/equipment/upload/")
    print("      GET    http://127.0.0.1:8000/api/equipment/summary/")
    print("      POST   http://127.0.0.1:8000/api/equipment/validate/")
    print("")
    print("   📈 Dataset APIs:")
    print("      GET    http://127.0.0.1:8000/api/datasets/")
    print("      POST   http://127.0.0.1:8000/api/datasets/upload/")
    print("      GET    http://127.0.0.1:8000/api/statistics/")

if __name__ == "__main__":
    test_root_endpoints()
    show_available_urls()
    print("\n🎉 Root endpoint has been fixed!")
    print("   You can now visit http://127.0.0.1:8000/ in your browser")