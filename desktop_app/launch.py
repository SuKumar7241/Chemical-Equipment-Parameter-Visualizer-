#!/usr/bin/env python3
"""
Desktop Application Launcher with Prerequisites Check
"""

import sys
import os
import subprocess
import time

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.7+ required.")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    dependencies = [
        ('PyQt5', 'PyQt5'),
        ('matplotlib', 'matplotlib'),
        ('requests', 'requests'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy')
    ]
    
    missing = []
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"✓ {name} - OK")
        except ImportError:
            print(f"❌ {name} - MISSING")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    return True

def check_backend():
    """Check if Django backend is running"""
    try:
        import requests
        print("  Testing connection to http://localhost:8000/...")
        # Test the root endpoint which should redirect or return something
        response = requests.get('http://localhost:8000/', timeout=5)
        print(f"  Response status: {response.status_code}")
        if response.status_code in [200, 302, 401]:  # Any of these means server is running
            print("✓ Django backend - RUNNING")
            return True
        else:
            print(f"❌ Django backend - HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Django backend - CONNECTION ERROR: {e}")
        print("Start with: cd datasetapi && python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Django backend - ERROR: {e}")
        return False

def launch_application():
    """Launch the main application"""
    print("\n🚀 Launching Dataset Analyzer Desktop Application...")
    try:
        # Import and run the main application
        from main import main
        main()
    except Exception as e:
        print(f"❌ Failed to launch application: {e}")
        return False
    return True

def main():
    print("=== Dataset Analyzer Desktop Launcher ===\n")
    
    # Check prerequisites
    print("Checking prerequisites...\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Backend Connection", check_backend)
    ]
    
    all_good = True
    for name, check_func in checks:
        print(f"Checking {name}...")
        if not check_func():
            all_good = False
        print()
    
    if all_good:
        print("✅ All prerequisites met!")
        print("=" * 50)
        launch_application()
    else:
        print("❌ Prerequisites not met. Please fix the issues above.")
        print("\nQuick fixes:")
        print("1. Install missing dependencies: pip install PyQt5 matplotlib requests pandas numpy")
        print("2. Start Django backend: cd datasetapi && python manage.py runserver")
        print("3. Run this launcher again: python launch.py")
        
        input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()