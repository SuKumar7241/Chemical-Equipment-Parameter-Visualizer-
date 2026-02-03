#!/usr/bin/env python3
"""
Demo script to test matplotlib app with sample data
"""

import sys
import os
import csv
import requests
import time
from pathlib import Path

def create_sample_data():
    """Create sample CSV data for testing"""
    sample_file = Path("demo_sample.csv")
    
    # Sample data with different data types and some missing values
    data = [
        ["id", "name", "age", "salary", "department", "rating"],
        ["1", "Alice Johnson", "28", "75000", "Engineering", "4.5"],
        ["2", "Bob Smith", "35", "82000", "Marketing", "4.2"],
        ["3", "Carol Davis", "", "68000", "Engineering", "4.8"],  # Missing age
        ["4", "David Wilson", "42", "95000", "Sales", ""],        # Missing rating
        ["5", "Eva Brown", "29", "", "Marketing", "4.1"],        # Missing salary
        ["6", "Frank Miller", "38", "71000", "Engineering", "4.6"],
        ["7", "Grace Lee", "31", "79000", "Sales", "4.3"],
        ["8", "Henry Taylor", "45", "88000", "", "4.7"],         # Missing department
        ["9", "Ivy Chen", "26", "63000", "Marketing", "4.0"],
        ["10", "Jack Anderson", "33", "77000", "Engineering", "4.4"]
    ]
    
    with open(sample_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    print(f"✅ Created sample data: {sample_file}")
    return sample_file

def test_backend_connection():
    """Test if backend is running"""
    try:
        response = requests.get("http://localhost:8000/api/datasets/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
        else:
            print(f"⚠️  Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        print("   Make sure to run: python datasetapi/start_server.py")
        return False

def upload_sample_data(file_path):
    """Upload sample data to backend"""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'name': 'Demo Dataset for Matplotlib'}
            
            response = requests.post(
                "http://localhost:8000/api/datasets/upload/",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Sample data uploaded successfully!")
                print(f"   Dataset ID: {result.get('id')}")
                return result
            else:
                print(f"❌ Upload failed with status: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def main():
    """Main demo function"""
    print("🎯 MATPLOTLIB APP DEMO SETUP")
    print("=" * 50)
    
    # Step 1: Check backend connection
    print("\n1. Checking backend connection...")
    if not test_backend_connection():
        print("\n❌ Backend is not running. Please start it first:")
        print("   python datasetapi/start_server.py")
        return False
    
    # Step 2: Create sample data
    print("\n2. Creating sample data...")
    sample_file = create_sample_data()
    
    # Step 3: Upload sample data
    print("\n3. Uploading sample data...")
    result = upload_sample_data(sample_file)
    
    if result:
        print("\n🎉 DEMO SETUP COMPLETE!")
        print("=" * 50)
        print("Now you can run the matplotlib app:")
        print("   python desktop_app/matplotlib_app.py")
        print("")
        print("Demo flow:")
        print("1. Login with any username/password (or register)")
        print("2. Go to 'Datasets' tab")
        print("3. Click 'Analyze' button")
        print("4. See matplotlib charts appear!")
        print("")
        print("Expected charts:")
        print("• Pie chart: Data types (int64, float64, object)")
        print("• Bar chart: Missing values (age, salary, department, rating)")
        print("• Bar chart: Numeric means (id, age, salary, rating)")
        print("• Text summary: Dataset overview")
        
        # Clean up
        try:
            os.remove(sample_file)
            print(f"\n🧹 Cleaned up temporary file: {sample_file}")
        except:
            pass
        
        return True
    else:
        print("\n❌ Demo setup failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)