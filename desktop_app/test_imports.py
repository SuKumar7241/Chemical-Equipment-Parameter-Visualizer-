#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

def test_imports():
    """Test all required imports"""
    try:
        print("Testing PyQt5 imports...")
        from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
        from PyQt5.QtCore import Qt, pyqtSignal, QThread
        from PyQt5.QtGui import QFont
        print("PyQt5 imports successful")
        
        print("Testing matplotlib imports...")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        print("Matplotlib imports successful")
        
        print("Testing other dependencies...")
        import requests
        import pandas as pd
        import numpy as np
        print("Other dependencies successful")
        
        print("Testing custom modules...")
        from services.api_client import APIClient
        from services.auth_service import AuthService
        from services.dataset_service import DatasetService
        print("Custom service modules successful")
        
        from ui.login_window import LoginWindow
        from ui.main_window import MainWindow
        print("UI modules successful")
        
        print("\nAll imports successful! The desktop application should work correctly.")
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def test_api_connection():
    """Test API connection"""
    try:
        print("\nTesting API connection...")
        from services.api_client import APIClient
        
        client = APIClient()
        # Test a simple endpoint that doesn't require authentication
        response = client.get('/api/')
        print("API connection successful")
        print(f"API Response: {response}")
        return True
        
    except Exception as e:
        print(f"API connection failed: {e}")
        print("Make sure the Django backend is running on http://localhost:8000")
        return False

if __name__ == '__main__':
    print("=== Desktop Application Test ===\n")
    
    imports_ok = test_imports()
    api_ok = test_api_connection()
    
    print(f"\n=== Test Results ===")
    print(f"Imports: {'PASS' if imports_ok else 'FAIL'}")
    print(f"API Connection: {'PASS' if api_ok else 'FAIL'}")
    
    if imports_ok and api_ok:
        print("\nDesktop application is ready to run!")
        print("Execute: python main.py")
    else:
        print("\nPlease fix the issues above before running the application.")