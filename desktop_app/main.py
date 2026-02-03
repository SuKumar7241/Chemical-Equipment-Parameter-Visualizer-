#!/usr/bin/env python3
"""
Dataset Analyzer Desktop Application
PyQt5 application that consumes Django REST APIs
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from services.auth_service import AuthService


class DatasetAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth_service = AuthService()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Dataset Analyzer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create stacked widget to switch between login and main windows
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create login window
        self.login_window = LoginWindow(self.auth_service)
        self.login_window.login_successful.connect(self.show_main_window)
        
        # Create main window (will be shown after login)
        self.main_window = None
        
        # Add login window to stack
        self.stacked_widget.addWidget(self.login_window)
        
        # Check if already logged in
        if self.auth_service.is_authenticated():
            self.show_main_window()
        
    def show_main_window(self):
        """Show main application window after successful login"""
        if self.main_window is None:
            self.main_window = MainWindow(self.auth_service)
            self.main_window.logout_requested.connect(self.show_login_window)
            self.stacked_widget.addWidget(self.main_window)
        
        self.stacked_widget.setCurrentWidget(self.main_window)
        
    def show_login_window(self):
        """Show login window after logout"""
        self.stacked_widget.setCurrentWidget(self.login_window)
        self.login_window.clear_form()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Dataset Analyzer")
    app.setOrganizationName("Dataset Analyzer")
    
    # Set application style
    app.setStyle('Fusion')
    
    window = DatasetAnalyzerApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()