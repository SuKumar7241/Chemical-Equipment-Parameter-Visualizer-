#!/usr/bin/env python3
"""
Direct test of the data summary API
"""

import requests

def test_direct():
    """Test the API directly"""
    
    print("Testing direct API calls...")
    
    # Test the list endpoint
    print("\n1. Testing /api/data-summaries/")
    try:
        response = requests.get("http://localhost:8000/api/data-summaries/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Count: {data.get('count', 0)}")
            if data.get('summaries'):
                print(f"First summary dataset_id: {data['summaries'][0]['dataset_id']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test specific dataset
    print("\n2. Testing /api/data-summary/1/")
    try:
        response = requests.get("http://localhost:8000/api/data-summary/1/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test specific dataset
    print("\n3. Testing /api/data-summary/3/")
    try:
        response = requests.get("http://localhost:8000/api/data-summary/3/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_direct()