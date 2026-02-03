#!/usr/bin/env python3
"""
Test script for matplotlib integration in desktop app
"""

import sys
import os
import traceback

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        # Set matplotlib backend first
        import matplotlib
        matplotlib.use('Qt5Agg')
        print(f"✓ matplotlib backend set to: {matplotlib.get_backend()}")
        
        # Test PyQt5
        from PyQt5.QtWidgets import QApplication, QWidget
        print("✓ PyQt5 imported successfully")
        
        # Test matplotlib components
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        print("✓ matplotlib components imported successfully")
        
        # Test other dependencies
        import numpy as np
        import pandas as pd
        import requests
        print("✓ numpy, pandas, requests imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        traceback.print_exc()
        return False

def test_matplotlib_qt_integration():
    """Test matplotlib Qt5 integration"""
    print("\nTesting matplotlib Qt5 integration...")
    
    try:
        # Set backend
        import matplotlib
        matplotlib.use('Qt5Agg')
        
        from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        import numpy as np
        
        # Create QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create a test widget with matplotlib
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Create matplotlib figure
        figure = Figure(figsize=(8, 6))
        canvas = FigureCanvas(figure)
        
        # Create a simple plot
        ax = figure.add_subplot(111)
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y, 'b-', label='sin(x)')
        ax.set_title('Test Plot')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.legend()
        ax.grid(True)
        
        # Add to layout
        layout.addWidget(canvas)
        widget.setLayout(layout)
        
        # Draw the canvas
        canvas.draw()
        
        print("✓ matplotlib Qt5 integration working")
        print(f"✓ Figure created with backend: {matplotlib.get_backend()}")
        
        # Clean up
        widget.close()
        
        return True
        
    except Exception as e:
        print(f"✗ matplotlib Qt5 integration error: {e}")
        traceback.print_exc()
        return False

def test_chart_widget():
    """Test the ChartWidget class"""
    print("\nTesting ChartWidget class...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from matplotlib_app import ChartWidget
        from PyQt5.QtWidgets import QApplication
        
        # Create QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create ChartWidget
        chart_widget = ChartWidget()
        
        # Test with sample data
        sample_statistics = {
            'column1': {
                'dtype': 'float64',
                'mean': 25.5,
                'std': 10.2,
                'min': 1.0,
                'max': 50.0,
                'null_count': 0
            },
            'column2': {
                'dtype': 'int64',
                'mean': 100.0,
                'std': 25.0,
                'min': 50,
                'max': 150,
                'null_count': 2
            },
            'column3': {
                'dtype': 'object',
                'null_count': 1
            }
        }
        
        sample_columns = ['column1', 'column2', 'column3']
        
        # Display analysis
        chart_widget.display_dataset_analysis(sample_statistics, sample_columns)
        
        print("✓ ChartWidget created and analysis displayed successfully")
        
        # Clean up
        chart_widget.close()
        
        return True
        
    except Exception as e:
        print(f"✗ ChartWidget test error: {e}")
        traceback.print_exc()
        return False

def test_services():
    """Test service imports"""
    print("\nTesting service imports...")
    
    try:
        # Add services directory to path
        services_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services')
        sys.path.insert(0, services_path)
        
        from auth_service import AuthService
        from api_client import APIClient
        from dataset_service import DatasetService
        
        print("✓ All services imported successfully")
        
        # Test service initialization
        auth_service = AuthService()
        api_client = APIClient()
        dataset_service = DatasetService(api_client)
        
        print("✓ All services initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Service test error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("MATPLOTLIB DESKTOP APP TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Matplotlib Qt5 Integration", test_matplotlib_qt_integration),
        ("ChartWidget Test", test_chart_widget),
        ("Services Test", test_services)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        print(f"Running: {test_name}")
        print(f"{'-' * 40}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'=' * 60}")
    print("TEST RESULTS SUMMARY")
    print(f"{'=' * 60}")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The matplotlib app should work correctly.")
        print("\nTo run the app:")
        print("1. Run: python matplotlib_app.py")
        print("2. Or use: run_matplotlib_app.bat")
    else:
        print(f"\n❌ {failed} test(s) failed. Please fix the issues before running the app.")
    
    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)