#!/usr/bin/env python3
"""
Fixed version without Unicode characters that cause encoding issues
"""

import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QLineEdit, QPushButton, QMessageBox,
                             QTabWidget, QFormLayout, QTextEdit, QTableWidget,
                             QTableWidgetItem, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

class LoginWorker(QThread):
    """Worker thread for login"""
    finished = pyqtSignal(dict)
    
    def __init__(self, username, password, action='login'):
        super().__init__()
        self.username = username
        self.password = password
        self.action = action
    
    def run(self):
        try:
            if self.action == 'login':
                response = requests.post('http://localhost:8000/api/auth/login/', {
                    'username': self.username,
                    'password': self.password
                }, timeout=10)
            else:  # register
                response = requests.post('http://localhost:8000/api/auth/register/', {
                    'username': self.username,
                    'password': self.password,
                    'email': f'{self.username}@example.com'
                }, timeout=10)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.finished.emit({'success': True, 'data': data})
            else:
                self.finished.emit({'success': False, 'error': f'HTTP {response.status_code}'})
                
        except Exception as e:
            self.finished.emit({'success': False, 'error': str(e)})

class DatasetAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.access_token = None
        self.current_user = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Dataset Analyzer - Fixed Version")
        self.setGeometry(200, 200, 1000, 700)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        self.create_login_tab()
        self.create_dashboard_tab()
        self.create_upload_tab()
        
        # Initially show only login tab
        self.tabs.setTabEnabled(1, False)  # Dashboard
        self.tabs.setTabEnabled(2, False)  # Upload
    
    def create_login_tab(self):
        """Create login tab"""
        login_widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Dataset Analyzer")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin: 30px;")
        layout.addWidget(title)
        
        # Login form
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password")
        form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.handle_register)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.register_btn)
        layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("Enter credentials to connect to Django backend")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; margin: 20px; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        login_widget.setLayout(layout)
        self.tabs.addTab(login_widget, "Login")
    
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        dashboard_widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        layout.addWidget(title)
        
        self.welcome_label = QLabel("Welcome!")
        self.welcome_label.setFont(QFont("Arial", 16))
        self.welcome_label.setStyleSheet("color: #27ae60; margin: 10px;")
        layout.addWidget(self.welcome_label)
        
        # Dataset list
        self.dataset_table = QTableWidget()
        self.dataset_table.setColumnCount(4)
        self.dataset_table.setHorizontalHeaderLabels(["Name", "File", "Rows", "Upload Date"])
        layout.addWidget(self.dataset_table)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Datasets")
        refresh_btn.clicked.connect(self.load_datasets)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        layout.addWidget(refresh_btn)
        
        dashboard_widget.setLayout(layout)
        self.tabs.addTab(dashboard_widget, "Dashboard")
    
    def create_upload_tab(self):
        """Create upload tab"""
        upload_widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Upload CSV Dataset")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        layout.addWidget(title)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #7f8c8d; padding: 10px;")
        
        select_btn = QPushButton("Select CSV File")
        select_btn.clicked.connect(self.select_file)
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(select_btn)
        layout.addLayout(file_layout)
        
        # Dataset name
        name_layout = QFormLayout()
        self.dataset_name = QLineEdit()
        self.dataset_name.setPlaceholderText("Enter dataset name")
        name_layout.addRow("Dataset Name:", self.dataset_name)
        layout.addLayout(name_layout)
        
        # Upload button
        self.upload_btn = QPushButton("Upload Dataset")
        self.upload_btn.clicked.connect(self.upload_file)
        self.upload_btn.setEnabled(False)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        layout.addWidget(self.upload_btn)
        
        layout.addStretch()
        upload_widget.setLayout(layout)
        self.tabs.addTab(upload_widget, "Upload")
        
        self.selected_file = None
    
    def handle_login(self):
        """Handle login"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
        
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Logging in...")
        self.status_label.setText("Connecting to Django backend...")
        
        self.login_worker = LoginWorker(username, password, 'login')
        self.login_worker.finished.connect(self.on_auth_finished)
        self.login_worker.start()
    
    def handle_register(self):
        """Handle registration"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
        
        self.register_btn.setEnabled(False)
        self.register_btn.setText("Registering...")
        self.status_label.setText("Creating account on Django backend...")
        
        self.login_worker = LoginWorker(username, password, 'register')
        self.login_worker.finished.connect(self.on_auth_finished)
        self.login_worker.start()
    
    def on_auth_finished(self, result):
        """Handle authentication result"""
        self.login_btn.setEnabled(True)
        self.login_btn.setText("Login")
        self.register_btn.setEnabled(True)
        self.register_btn.setText("Register")
        
        if result['success']:
            data = result['data']
            self.current_user = data.get('user', {})
            tokens = data.get('tokens', {})
            self.access_token = tokens.get('access')
            
            self.status_label.setText("Authentication successful!")
            self.welcome_label.setText(f"Welcome, {self.current_user.get('username', 'User')}!")
            
            # Enable other tabs
            self.tabs.setTabEnabled(1, True)
            self.tabs.setTabEnabled(2, True)
            self.tabs.setCurrentIndex(1)  # Switch to dashboard
            
            # Load initial data
            self.load_datasets()
            
        else:
            error = result.get('error', 'Unknown error')
            self.status_label.setText(f"Authentication failed: {error}")
            QMessageBox.critical(self, "Authentication Failed", f"Error: {error}")
    
    def load_datasets(self):
        """Load datasets from backend"""
        if not self.access_token:
            return
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get('http://localhost:8000/api/datasets/', headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                datasets = data.get('results', [])
                
                self.dataset_table.setRowCount(len(datasets))
                for row, dataset in enumerate(datasets):
                    self.dataset_table.setItem(row, 0, QTableWidgetItem(dataset.get('name', 'Unnamed')))
                    self.dataset_table.setItem(row, 1, QTableWidgetItem(dataset.get('file_name', '')))
                    self.dataset_table.setItem(row, 2, QTableWidgetItem(str(dataset.get('total_rows', 0))))
                    self.dataset_table.setItem(row, 3, QTableWidgetItem(dataset.get('upload_date', '')[:10]))
                
                self.status_label.setText(f"Loaded {len(datasets)} datasets")
            else:
                self.status_label.setText(f"Failed to load datasets: HTTP {response.status_code}")
                
        except Exception as e:
            self.status_label.setText(f"Error loading datasets: {str(e)}")
    
    def select_file(self):
        """Select CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.selected_file = file_path
            import os
            self.file_label.setText(f"Selected: {os.path.basename(file_path)}")
            self.upload_btn.setEnabled(True)
    
    def upload_file(self):
        """Upload selected file"""
        if not self.selected_file or not self.access_token:
            return
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            with open(self.selected_file, 'rb') as f:
                files = {'file': f}
                data = {'name': self.dataset_name.text() or 'Uploaded Dataset'}
                
                response = requests.post('http://localhost:8000/api/datasets/upload/', 
                                       headers=headers, files=files, data=data, timeout=30)
            
            if response.status_code in [200, 201]:
                QMessageBox.information(self, "Success", "Dataset uploaded successfully!")
                self.load_datasets()  # Refresh the list
                self.selected_file = None
                self.file_label.setText("No file selected")
                self.dataset_name.clear()
                self.upload_btn.setEnabled(False)
            else:
                QMessageBox.critical(self, "Upload Failed", f"HTTP {response.status_code}")
                
        except Exception as e:
            QMessageBox.critical(self, "Upload Error", str(e))

def main():
    print("=== Dataset Analyzer - Fixed Version ===")
    print("Starting application with Django backend integration...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Dataset Analyzer - Fixed")
    app.setStyle('Fusion')
    
    window = DatasetAnalyzerApp()
    window.show()
    window.raise_()
    window.activateWindow()
    
    print("Application window should be visible!")
    print("This version includes Django backend connectivity")
    print("You can login, view datasets, and upload CSV files")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()