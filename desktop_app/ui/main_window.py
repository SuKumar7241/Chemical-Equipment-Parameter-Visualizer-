"""
Main application window
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QMenuBar, QAction, QMessageBox, QLabel, QFrame)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont

from services.auth_service import AuthService
from services.dataset_service import DatasetService
from .dashboard_tab import DashboardTab
from .upload_tab import UploadTab
from .datasets_tab import DatasetsTab
from .history_tab import HistoryTab


class MainWindow(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.dataset_service = DatasetService(auth_service.get_api_client())
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header with user info and logout
        header = self.create_header()
        layout.addWidget(header)
        
        # Main tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.dashboard_tab = DashboardTab(self.dataset_service)
        self.upload_tab = UploadTab(self.dataset_service)
        self.datasets_tab = DatasetsTab(self.dataset_service)
        self.history_tab = HistoryTab(self.dataset_service)
        
        # Add tabs
        self.tab_widget.addTab(self.dashboard_tab, "Dashboard")
        self.tab_widget.addTab(self.upload_tab, "Upload")
        self.tab_widget.addTab(self.datasets_tab, "Datasets")
        self.tab_widget.addTab(self.history_tab, "History")
        
        # Connect signals
        self.upload_tab.upload_completed.connect(self.on_upload_completed)
        self.datasets_tab.dataset_deleted.connect(self.on_dataset_changed)
        self.history_tab.dataset_deleted.connect(self.on_dataset_changed)
        
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
        self.setWindowTitle("Chemical Equipment Parameter Visualizer")
    
    def create_header(self):
        """Create header with user info and logout button"""
        header = QFrame()
        header.setFrameStyle(QFrame.StyledPanel)
        header.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                color: white;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # App title
        title = QLabel("Chemical Equipment Parameter Visualizer")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # User info
        user = self.auth_service.get_current_user()
        if user:
            user_label = QLabel(f"Welcome, {user.get('username', 'User')}")
            user_label.setStyleSheet("color: white; margin-right: 20px;")
            layout.addWidget(user_label)
        
        # Logout button
        from PyQt5.QtWidgets import QPushButton
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.handle_logout)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(logout_btn)
        
        header.setLayout(layout)
        return header
    
    def handle_logout(self):
        """Handle logout"""
        reply = QMessageBox.question(self, 'Logout', 'Are you sure you want to logout?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.auth_service.logout()
            self.logout_requested.emit()
    
    def on_upload_completed(self):
        """Handle upload completion - refresh other tabs"""
        self.dashboard_tab.refresh_data()
        self.datasets_tab.refresh_data()
        self.history_tab.refresh_data()
    
    def on_dataset_changed(self):
        """Handle dataset changes - refresh other tabs"""
        self.dashboard_tab.refresh_data()
        self.datasets_tab.refresh_data()
        self.history_tab.refresh_data()
    
    def refresh_all_tabs(self):
        """Refresh all tabs"""
        self.dashboard_tab.refresh_data()
        self.datasets_tab.refresh_data()
        self.history_tab.refresh_data()