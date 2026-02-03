#!/usr/bin/env python3
"""
Test script for the new Data Summary API
Tests the API endpoints and validates responses
"""

import requests
import json
import sys
import os

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:8000"

def test_data_summary_api():
    """Test the Data Summary API endpoints"""
    
    print("=" * 60)
    print("TESTING DATA SUMMARY API")
    print("=" * 60)
    
    try:
        # Test 1: Get list of all dataset summaries
        print("\n1. Testing dataset summaries list endpoint...")
        response = requests.get(f"{BASE_URL}/api/data-summaries/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Successfully retrieved {data.get('count', 0)} dataset summaries")
            
            if data.get('summaries'):
                first_summary = data['summaries'][0]
                dataset_id = first_summary['dataset_id']
                print(f"✓ Found dataset ID {dataset_id} for detailed testing")
                
                # Test 2: Get specific dataset summary
                print(f"\n2. Testing specific dataset summary (ID: {dataset_id})...")
                detail_response = requests.get(f"{BASE_URL}/api/data-summary/{dataset_id}/")
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print("✓ Successfully retrieved detailed dataset summary")
                    
                    # Display the API response structure
                    print("\n" + "=" * 40)
                    print("EXAMPLE API RESPONSE JSON:")
                    print("=" * 40)
                    print(json.dumps(detail_data, indent=2))
                    
                    # Validate required fields
                    print("\n" + "=" * 40)
                    print("VALIDATION RESULTS:")
                    print("=" * 40)
                    
                    required_fields = ['total_records', 'averages', 'equipment_type_distribution']
                    for field in required_fields:
                        if field in detail_data:
                            print(f"✓ {field}: Present")
                        else:
                            print(f"✗ {field}: Missing")
                    
                    # Validate averages structure
                    if 'averages' in detail_data:
                        avg_fields = ['flowrate', 'pressure', 'temperature']
                        for avg_field in avg_fields:
                            if avg_field in detail_data['averages']:
                                value = detail_data['averages'][avg_field]
                                print(f"✓ averages.{avg_field}: {value}")
                            else:
                                print(f"✗ averages.{avg_field}: Missing")
                    
                    # Validate equipment distribution
                    if 'equipment_type_distribution' in detail_data:
                        equipment_dist = detail_data['equipment_type_distribution']
                        if equipment_dist:
                            print(f"✓ equipment_type_distribution: {len(equipment_dist)} types found")
                            for eq_type, count in equipment_dist.items():
                                print(f"  - {eq_type}: {count}")
                        else:
                            print("! equipment_type_distribution: Empty (no equipment types found)")
                    
                else:
                    print(f"✗ Failed to get dataset summary: {detail_response.status_code}")
                    print(f"Response: {detail_response.text}")
            else:
                print("! No datasets found for testing")
        else:
            print(f"✗ Failed to get summaries list: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed. Make sure the Django server is running:")
        print("  python datasetapi/start_server.py")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")

def create_example_response():
    """Create example API response JSON for documentation"""
    
    example_response = {
        "total_records": 1500,
        "averages": {
            "flowrate": 45.67,
            "pressure": 120.34,
            "temperature": 78.92
        },
        "equipment_type_distribution": {
            "Pump": 450,
            "Valve": 320,
            "Sensor": 280,
            "Controller": 250,
            "Motor": 200
        }
    }
    
    print("\n" + "=" * 60)
    print("EXAMPLE API RESPONSE JSON (for documentation):")
    print("=" * 60)
    print(json.dumps(example_response, indent=2))
    
    return example_response

def test_api_endpoints():
    """Test all related API endpoints"""
    
    print("\n" + "=" * 60)
    print("TESTING ALL DATA SUMMARY ENDPOINTS")
    print("=" * 60)
    
    endpoints = [
        ("GET", "/api/data-summaries/", "List all dataset summaries"),
        ("GET", "/api/data-summary/1/", "Get specific dataset summary (ID: 1)"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"\n{method} {endpoint}")
        print(f"Description: {description}")
        
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ Success")
            elif response.status_code == 404:
                print("! Not Found (expected if no data)")
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"✗ Request failed: {e}")

if __name__ == "__main__":
    print("Data Summary API Test Suite")
    print("Make sure Django server is running on localhost:8000")
    
    # Create example response for documentation
    create_example_response()
    
    # Test the actual API
    test_data_summary_api()
    
    # Test all endpoints
    test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)