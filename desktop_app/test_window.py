#!/usr/bin/env python3
"""
Simple test to check if PyQt5 can display windows
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt

def test_simple_window():
    """Test if we can show a simple PyQt5 window"""
    app = QApplication(sys.argv)
    
    # Create a simple window
    window = QWidget()
    window.setWindowTitle("PyQt5 Test Window")
    window.setGeometry(300, 300, 400, 200)
    
    # Add some content
    layout = QVBoxLayout()
    
    label = QLabel("If you can see this, PyQt5 is working!")
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("font-size: 16px; padding: 20px;")
    
    button = QPushButton("Close")
    button.clicked.connect(window.close)
    
    layout.addWidget(label)
    layout.addWidget(button)
    window.setLayout(layout)
    
    # Show the window
    window.show()
    window.raise_()  # Bring to front
    window.activateWindow()  # Make it active
    
    print("Test window should be visible now...")
    print("If you don't see it, there might be a display issue.")
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    test_simple_window()