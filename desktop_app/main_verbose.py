#!/usr/bin/env python3
"""
Verbose version of main.py with detailed logging
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

def main():
    print("=== Dataset Analyzer Desktop Application (Verbose Mode) ===")
    
    try:
        print("Step 1: Creating QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("Dataset Analyzer")
        app.setOrganizationName("Dataset Analyzer")
        app.setStyle('Fusion')
        print("QApplication created successfully")
        
        print("Step 2: Importing services...")
        from services.auth_service import AuthService
        print("AuthService imported")
        
        print("Step 3: Creating AuthService...")
        auth_service = AuthService()
        print("AuthService created")
        
        print("Step 4: Importing UI components...")
        from ui.login_window import LoginWindow
        from ui.main_window import MainWindow
        print("UI components imported")
        
        print("Step 5: Creating main application class...")
        
        class DatasetAnalyzerApp(QMainWindow):
            def __init__(self):
                super().__init__()
                print("  - Initializing main window...")
                self.auth_service = auth_service
                self.init_ui()
                
            def init_ui(self):
                print("  - Setting up UI...")
                self.setWindowTitle("Dataset Analyzer")
                self.setGeometry(100, 100, 1200, 800)
                
                # Create stacked widget
                self.stacked_widget = QStackedWidget()
                self.setCentralWidget(self.stacked_widget)
                
                print("  - Creating login window...")
                self.login_window = LoginWindow(self.auth_service)
                self.login_window.login_successful.connect(self.show_main_window)
                
                self.main_window = None
                self.stacked_widget.addWidget(self.login_window)
                
                print("  - Checking authentication...")
                if self.auth_service.is_authenticated():
                    print("  - User already authenticated, showing main window...")
                    self.show_main_window()
                else:
                    print("  - User not authenticated, showing login window...")
                
                print("  - UI setup complete")
                
            def show_main_window(self):
                print("  - Showing main window...")
                if self.main_window is None:
                    self.main_window = MainWindow(self.auth_service)
                    self.main_window.logout_requested.connect(self.show_login_window)
                    self.stacked_widget.addWidget(self.main_window)
                
                self.stacked_widget.setCurrentWidget(self.main_window)
                
            def show_login_window(self):
                print("  - Showing login window...")
                self.stacked_widget.setCurrentWidget(self.login_window)
                self.login_window.clear_form()
        
        print("Step 6: Creating application instance...")
        window = DatasetAnalyzerApp()
        print("Application instance created")
        
        print("Step 7: Showing window...")
        window.show()
        window.raise_()
        window.activateWindow()
        print("✓ Window should be visible now!")
        
        # Show a confirmation message
        print("Step 8: Showing confirmation dialog...")
        msg = QMessageBox()
        msg.setWindowTitle("Application Started")
        msg.setText("Desktop application is running!\n\nLook for the 'Dataset Analyzer' window.\nIf you don't see it, check your taskbar or press Alt+Tab.")
        msg.setIcon(QMessageBox.Information)
        msg.show()
        msg.raise_()
        msg.activateWindow()
        print("✓ Confirmation dialog shown")
        
        print("Step 9: Starting event loop...")
        result = app.exec_()
        print(f"Application exited with code: {result}")
        sys.exit(result)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("Full traceback:")
        traceback.print_exc()
        
        # Show error dialog if possible
        try:
            error_msg = QMessageBox()
            error_msg.setWindowTitle("Application Error")
            error_msg.setText(f"Failed to start application:\n\n{str(e)}")
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.exec_()
        except:
            pass
        
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()