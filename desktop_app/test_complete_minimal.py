#!/usr/bin/env python3
"""
Minimal test for complete_app.py to identify issues
"""

import sys
import traceback

def test_imports():
    """Test all imports"""
    print("Testing imports...")
    
    try:
        import requests
        print("✅ requests imported")
    except Exception as e:
        print(f"❌ requests failed: {e}")
        return False
    
    try:
        import matplotlib
        matplotlib.use('Qt5Agg')  # Set backend before importing pyplot
        import matplotlib.pyplot as plt
        print("✅ matplotlib imported")
    except Exception as e:
        print(f"❌ matplotlib failed: {e}")
        return False
    
    try:
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        print("✅ matplotlib Qt5 backend imported")
    except Exception as e:
        print(f"❌ matplotlib Qt5 backend failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported")
    except Exception as e:
        print(f"❌ numpy failed: {e}")
        return False
    
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
        from PyQt5.QtCore import Qt, QThread, pyqtSignal
        from PyQt5.QtGui import QFont
        print("✅ PyQt5 imported")
    except Exception as e:
        print(f"❌ PyQt5 failed: {e}")
        return False
    
    return True

def test_basic_app():
    """Test basic PyQt5 app creation"""
    print("\nTesting basic PyQt5 app...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
        
        app = QApplication(sys.argv)
        window = QMainWindow()
        window.setWindowTitle("Test Window")
        window.setCentralWidget(QLabel("Test"))
        
        print("✅ Basic PyQt5 app created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Basic PyQt5 app failed: {e}")
        traceback.print_exc()
        return False

def test_matplotlib_qt():
    """Test matplotlib with Qt5 backend"""
    print("\nTesting matplotlib with Qt5...")
    
    try:
        import matplotlib
        matplotlib.use('Qt5Agg')
        
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
        
        app = QApplication(sys.argv)
        
        window = QMainWindow()
        widget = QWidget()
        layout = QVBoxLayout()
        
        figure = Figure(figsize=(8, 6))
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
        
        widget.setLayout(layout)
        window.setCentralWidget(widget)
        
        print("✅ Matplotlib Qt5 integration successful")
        return True
        
    except Exception as e:
        print(f"❌ Matplotlib Qt5 integration failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("=== Complete App Minimal Test ===")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed")
        return False
    
    # Test basic app
    if not test_basic_app():
        print("\n❌ Basic app test failed")
        return False
    
    # Test matplotlib integration
    if not test_matplotlib_qt():
        print("\n❌ Matplotlib integration test failed")
        return False
    
    print("\n✅ All tests passed! complete_app.py should work.")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)