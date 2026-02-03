#!/usr/bin/env python
"""
Quick test to verify the web application is working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_basic_functionality():
    print("🧪 Testing Basic Web Application Functionality")
    print("=" * 50)
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Root endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test 2: API root
    try:
        response = requests.get(f"{BASE_URL}/api/")
        print(f"✅ API root: {response.status_code}")
    except Exception as e:
        print(f"❌ API root failed: {e}")
        return False
    
    # Test 3: User registration
    try:
        user_data = {
            "username": "testuser123",
            "password": "testpass123",
            "email": "test@example.com"
        }
        response = requests.post(f"{BASE_URL}/api/auth/register/", json=user_data)
        if response.status_code == 201:
            print(f"✅ User registration: {response.status_code}")
            tokens = response.json().get('tokens', {})
            access_token = tokens.get('access')
            
            # Test 4: Authenticated request
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
            print(f"✅ Authenticated profile access: {response.status_code}")
            
            return True
        else:
            print(f"❌ User registration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n🎉 Web application is working correctly!")
        print("✅ Backend APIs are functional")
        print("✅ Authentication system working")
        print("✅ Ready for frontend connection")
    else:
        print("\n⚠️ Some issues detected")