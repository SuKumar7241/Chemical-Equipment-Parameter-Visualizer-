#!/usr/bin/env python3
"""
Test script for the fixed complete app (without matplotlib)
"""

import sys
import os

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5.QtWidgets imported successfully")
    except ImportError as e:
        print(f"✗ PyQt5.QtWidgets import failed: {e}")
        return False
    
    try:
        import requests
        print("✓ requests imported successfully")
    except ImportError as e:
        print(f"✗ requests import failed: {e}")
        return False
    
    # Test that matplotlib is NOT imported (this was causing the hang)
    if 'matplotlib' in sys.modules:
        print("⚠ matplotlib is already imported (this could cause issues)")
    else:
        print("✓ matplotlib not imported (good - avoiding Qt5 backend issues)")
    
    return True

def test_app_creation():
    """Test that the app can be created without hanging"""
    print("\nTesting app creation...")
    
    try:
        # Import the fixed app
        sys.path.insert(0, os.path.dirname(__file__))
        from complete_app_no_matplotlib import CompleteDatasetAnalyzer
        print("✓ CompleteDatasetAnalyzer imported successfully")
        
        # Import QApplication
        from PyQt5.QtWidgets import QApplication
        
        # Create QApplication
        app = QApplication([])
        print("✓ QApplication created successfully")
        
        # Create main window
        window = CompleteDatasetAnalyzer()
        print("✓ CompleteDatasetAnalyzer window created successfully")
        
        # Test window properties
        print(f"✓ Window title: {window.windowTitle()}")
        print(f"✓ Window size: {window.size().width()}x{window.size().height()}")
        print(f"✓ Number of tabs: {window.tabs.count()}")
        
        # Clean up
        window.close()
        app.quit()
        print("✓ App cleaned up successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=== Testing Fixed Complete App ===")
    print("This test verifies the app can start without hanging")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed")
        return 1
    
    # Test app creation
    if not test_app_creation():
        print("\n❌ App creation test failed")
        return 1
    
    print("\n✅ All tests passed!")
    print("The fixed app should now work without hanging.")
    print("\nTo run the fixed app:")
    print("python desktop_app/complete_app_no_matplotlib.py")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())