#!/usr/bin/env python
"""
Server startup script with helpful information
"""
import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check if migrations are applied
    if not Path('db.sqlite3').exists():
        print("⚠️  Database not found. Running migrations...")
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("✅ Database created successfully!")
    
    # Check for sample data
    sample_files = ['sample_equipment_data.csv', 'sample_data.csv']
    sample_found = any(Path(f).exists() for f in sample_files)
    
    if not sample_found:
        print("📥 Sample data not found.")
        print("   Download sample_equipment_data.csv from:")
        print("   https://drive.google.com/file/d/1cq26Jb7vQ8RC1POISdGic0jr_tuTJI1E/view")
        print("   Or run: python demo_upload.py to test with existing data")
    else:
        print("✅ Sample data found!")

def show_endpoints():
    """Display available API endpoints"""
    print("\n🌐 Available API Endpoints:")
    print("   📊 Datasets:")
    print("      GET    /api/datasets/                    - List all datasets")
    print("      POST   /api/datasets/upload/             - Upload new dataset")
    print("      GET    /api/datasets/{id}/               - Get dataset details")
    print("      GET    /api/datasets/{id}/statistics/    - Get dataset statistics")
    print("      GET    /api/datasets/{id}/columns/       - Get column information")
    print("      DELETE /api/datasets/{id}/delete_dataset/ - Delete dataset")
    
    print("\n   📈 Statistics:")
    print("      GET    /api/statistics/                  - List all statistics")
    print("      GET    /api/statistics/{id}/             - Get specific statistics")
    print("      GET    /api/statistics/{id}/numeric_summary/     - Numeric columns only")
    print("      GET    /api/statistics/{id}/categorical_summary/ - Categorical columns only")
    
    print("\n   📋 Columns:")
    print("      GET    /api/columns/                     - List all columns")
    print("      GET    /api/columns/?dataset={id}        - Get columns for dataset")

def show_testing_commands():
    """Show testing commands"""
    print("\n🧪 Testing Commands:")
    print("   # Test the setup")
    print("   python test_api.py")
    print("")
    print("   # Demo with sample data")
    print("   python demo_upload.py")
    print("")
    print("   # Upload via curl")
    print("   curl -X POST http://localhost:8000/api/datasets/upload/ \\")
    print("     -F \"file=@sample_equipment_data.csv\" \\")
    print("     -F \"name=Equipment Dataset\"")

def main():
    """Main function"""
    print("🚀 Chemical Equipment Parameter Visualizer API")
    print("=" * 50)
    
    # Change to the script directory (datasetapi folder)
    script_dir = Path(__file__).parent
    original_dir = Path.cwd()
    os.chdir(script_dir)
    print(f"📁 Working directory: {Path.cwd()}")
    
    check_requirements()
    show_endpoints()
    show_testing_commands()
    
    print("\n🎯 Quick Start:")
    print("   1. Download sample_equipment_data.csv (see link above)")
    print("   2. Run: python demo_upload.py")
    print("   3. Visit: http://localhost:8000/admin/ (create superuser first)")
    print("   4. Test APIs using the endpoints listed above")
    
    print("\n🔥 Starting Django development server...")
    print("   Server will be available at: http://localhost:8000/")
    print("   Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the Django development server
        subprocess.run([sys.executable, 'manage.py', 'runserver'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting server: {e}")
        print("   Make sure you're in the datasetapi directory")
        print("   Try: python manage.py runserver")
    finally:
        # Change back to original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    main()