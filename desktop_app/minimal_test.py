#!/usr/bin/env python3
"""
Minimal test to diagnose the issue
"""

import sys

def test_step_by_step():
    print("=== Minimal Desktop App Test ===\n")
    
    # Step 1: Test PyQt5 import
    try:
        print("Step 1: Testing PyQt5 import...")
        from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
        from PyQt5.QtCore import Qt
        print("PyQt5 import successful")
    except Exception as e:
        print(f"PyQt5 import failed: {e}")
        return False
    
    # Step 2: Create QApplication
    try:
        print("Step 2: Creating QApplication...")
        app = QApplication(sys.argv)
        print("QApplication created")
    except Exception as e:
        print(f"QApplication creation failed: {e}")
        return False
    
    # Step 3: Create simple window
    try:
        print("Step 3: Creating simple window...")
        
        window = QWidget()
        window.setWindowTitle("Minimal Test - Dataset Analyzer")
        window.setGeometry(300, 300, 500, 300)
        
        layout = QVBoxLayout()
        
        title = QLabel("Desktop App Test")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 20px;")
        
        message = QLabel("If you can see this window, PyQt5 is working correctly!")
        message.setAlignment(Qt.AlignCenter)
        message.setStyleSheet("font-size: 14px; color: #7f8c8d; margin: 20px;")
        
        test_btn = QPushButton("Test Button")
        test_btn.clicked.connect(lambda: print("Button clicked!"))
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(window.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        layout.addWidget(title)
        layout.addWidget(message)
        layout.addWidget(test_btn)
        layout.addWidget(close_btn)
        
        window.setLayout(layout)
        print("Window created")
        
    except Exception as e:
        print(f"Window creation failed: {e}")
        return False
    
    # Step 4: Show window
    try:
        print("Step 4: Showing window...")
        window.show()
        window.raise_()
        window.activateWindow()
        print("Window should be visible now!")
        print("Look for 'Minimal Test - Dataset Analyzer' window")
        
    except Exception as e:
        print(f"Window display failed: {e}")
        return False
    
    # Step 5: Run event loop
    try:
        print("Step 5: Starting event loop...")
        print("Application is running. Close the window to exit.")
        result = app.exec_()
        print(f"Application exited with code: {result}")
        return True
        
    except Exception as e:
        print(f"Event loop failed: {e}")
        return False

if __name__ == '__main__':
    success = test_step_by_step()
    
    if success:
        print("\nMinimal test completed successfully!")
        print("PyQt5 is working correctly on your system.")
    else:
        print("\nMinimal test failed.")
        print("There's an issue with PyQt5 setup.")
    
    input("Press Enter to exit...")