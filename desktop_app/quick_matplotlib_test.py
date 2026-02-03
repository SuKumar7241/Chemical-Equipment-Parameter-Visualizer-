#!/usr/bin/env python3
"""
Quick test for matplotlib integration
"""

import sys
import os

def test_basic_matplotlib():
    """Test basic matplotlib functionality"""
    try:
        # Set backend first
        import matplotlib
        matplotlib.use('Qt5Agg')
        print(f"✓ Matplotlib backend: {matplotlib.get_backend()}")
        
        # Test imports
        from PyQt5.QtWidgets import QApplication
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        import numpy as np
        
        print("✓ All imports successful")
        
        # Create simple figure
        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        
        # Sample data
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y, 'b-', label='sin(x)')
        ax.set_title('Test Chart')
        ax.legend()
        
        print("✓ Chart created successfully")
        print("✓ Matplotlib integration is working!")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    print("Testing matplotlib integration...")
    success = test_basic_matplotlib()
    
    if success:
        print("\n🎉 Matplotlib is ready for the desktop app!")
        print("You can now run: python desktop_app/matplotlib_app.py")
    else:
        print("\n❌ Matplotlib integration failed")
    
    sys.exit(0 if success else 1)