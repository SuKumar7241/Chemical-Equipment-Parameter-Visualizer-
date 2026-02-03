#!/usr/bin/env python3
"""
Complete Desktop Application - Fixed Version (No Matplotlib)
Removes matplotlib integration to avoid Qt5 backend hanging issues
"""

import sys
import requests
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QLineEdit, QPushButton, QMessageBox,
                             QTabWidget, QFormLayout, QTextEdit, QTableWidget,
                             QTableWidgetItem, QFileDialog, QScrollArea, QFrame,
                             QSplitter, QHeaderView, QAbstractItemView, QDialog,
                             QListWidget, QDialogButtonBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

class AuthWorker(QThread):
    """Worker thread for authentication"""
    finished = pyqtSignal(dict)
    
    def __init__(self, username, password, action='login'):
        super().__init__()
        self.username = username
        self.password = password
        self.action = action
        self.setTerminationEnabled(True)
    
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
    
    def __del__(self):
        """Ensure proper cleanup"""
        if self.isRunning():
            self.terminate()
            self.wait()

class DataWorker(QThread):
    """Worker thread for data operations"""
    finished = pyqtSignal(dict)
    
    def __init__(self, token, operation, **kwargs):
        super().__init__()
        self.token = token
        self.operation = operation
        self.kwargs = kwargs
        self.setTerminationEnabled(True)
    
    def run(self):
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            if self.operation == 'load_datasets':
                response = requests.get('http://localhost:8000/api/datasets/', headers=headers, timeout=10)
            elif self.operation == 'load_history':
                page = self.kwargs.get('page', 1)
                response = requests.get(f'http://localhost:8000/api/history/datasets/?page={page}&page_size=10', 
                                      headers=headers, timeout=10)
            elif self.operation == 'load_dataset_detail':
                dataset_id = self.kwargs['dataset_id']
                response = requests.get(f'http://localhost:8000/api/datasets/{dataset_id}/', headers=headers, timeout=10)
            elif self.operation == 'load_statistics':
                dataset_id = self.kwargs['dataset_id']
                response = requests.get(f'http://localhost:8000/api/datasets/{dataset_id}/statistics/', 
                                      headers=headers, timeout=10)
            elif self.operation == 'load_columns':
                dataset_id = self.kwargs['dataset_id']
                response = requests.get(f'http://localhost:8000/api/datasets/{dataset_id}/columns/', 
                                      headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.finished.emit({'success': True, 'data': response.json()})
            else:
                self.finished.emit({'success': False, 'error': f'HTTP {response.status_code}'})
                
        except Exception as e:
            self.finished.emit({'success': False, 'error': str(e)})
    
    def __del__(self):
        """Ensure proper cleanup"""
        if self.isRunning():
            self.terminate()
            self.wait()

class StatCard(QFrame):
    """Statistics card widget"""
    
    def __init__(self, title, value, color="#3498db"):
        super().__init__()
        self.init_ui(title, value, color)
    
    def init_ui(self, title, value, color):
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Value
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Arial", 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11))
        title_label.setStyleSheet("color: #7f8c8d;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        self.setLayout(layout)
        self.setFixedHeight(100)

class DataAnalysisWidget(QWidget):
    """Widget for displaying data analysis without matplotlib"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Data Analysis Summary")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px;")
        layout.addWidget(title)
        
        # Analysis content area
        self.analysis_area = QScrollArea()
        self.analysis_content = QWidget()
        self.analysis_layout = QVBoxLayout()
        self.analysis_content.setLayout(self.analysis_layout)
        self.analysis_area.setWidget(self.analysis_content)
        self.analysis_area.setWidgetResizable(True)
        layout.addWidget(self.analysis_area)
        
        self.setLayout(layout)
    
    def clear_analysis(self):
        """Clear the analysis display"""
        for i in reversed(range(self.analysis_layout.count())):
            child = self.analysis_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
    
    def display_dataset_analysis(self, statistics, columns):
        """Display dataset analysis as text and tables"""
        self.clear_analysis()
        
        if not statistics or not columns:
            no_data_label = QLabel("No data available for analysis")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #7f8c8d; font-size: 14px; padding: 20px;")
            self.analysis_layout.addWidget(no_data_label)
            return
        
        # Dataset Overview
        overview_frame = QFrame()
        overview_frame.setFrameStyle(QFrame.StyledPanel)
        overview_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 10px;")
        overview_layout = QVBoxLayout()
        
        overview_title = QLabel("Dataset Overview")
        overview_title.setFont(QFont("Arial", 14, QFont.Bold))
        overview_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        overview_layout.addWidget(overview_title)
        
        # Basic statistics
        stats_text = f"""
        Total Records: {statistics.get('total_records', 0):,}
        Numeric Columns: {statistics.get('numeric_columns_count', 0)}
        Categorical Columns: {statistics.get('categorical_columns_count', 0)}
        Missing Values: {statistics.get('missing_values_count', 0):,}
        """
        
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("font-family: monospace; background-color: white; padding: 10px; border-radius: 3px;")
        overview_layout.addWidget(stats_label)
        
        overview_frame.setLayout(overview_layout)
        self.analysis_layout.addWidget(overview_frame)
        
        # Data Types Analysis
        types_frame = QFrame()
        types_frame.setFrameStyle(QFrame.StyledPanel)
        types_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 10px;")
        types_layout = QVBoxLayout()
        
        types_title = QLabel("Data Types Distribution")
        types_title.setFont(QFont("Arial", 14, QFont.Bold))
        types_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        types_layout.addWidget(types_title)
        
        # Count data types
        data_types = {}
        for col in columns:
            dtype = col.get('data_type', 'unknown')
            data_types[dtype] = data_types.get(dtype, 0) + 1
        
        types_text = ""
        for dtype, count in data_types.items():
            percentage = (count / len(columns)) * 100 if columns else 0
            types_text += f"{dtype.capitalize()}: {count} columns ({percentage:.1f}%)\n"
        
        types_label = QLabel(types_text)
        types_label.setStyleSheet("font-family: monospace; background-color: white; padding: 10px; border-radius: 3px;")
        types_layout.addWidget(types_label)
        
        types_frame.setLayout(types_layout)
        self.analysis_layout.addWidget(types_frame)
        
        # Missing Values Analysis
        missing_frame = QFrame()
        missing_frame.setFrameStyle(QFrame.StyledPanel)
        missing_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 10px;")
        missing_layout = QVBoxLayout()
        
        missing_title = QLabel("Missing Values Analysis")
        missing_title.setFont(QFont("Arial", 14, QFont.Bold))
        missing_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        missing_layout.addWidget(missing_title)
        
        # Create table for missing values
        missing_table = QTableWidget()
        missing_table.setColumnCount(3)
        missing_table.setHorizontalHeaderLabels(["Column", "Missing Count", "Percentage"])
        missing_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Filter columns with missing values
        missing_cols = [col for col in columns if col.get('null_count', 0) > 0]
        missing_table.setRowCount(len(missing_cols))
        
        total_records = statistics.get('total_records', 1)
        for row, col in enumerate(missing_cols):
            null_count = col.get('null_count', 0)
            percentage = (null_count / total_records) * 100 if total_records > 0 else 0
            
            missing_table.setItem(row, 0, QTableWidgetItem(col['column_name']))
            missing_table.setItem(row, 1, QTableWidgetItem(str(null_count)))
            missing_table.setItem(row, 2, QTableWidgetItem(f"{percentage:.2f}%"))
        
        missing_table.setMaximumHeight(200)
        missing_layout.addWidget(missing_table)
        
        missing_frame.setLayout(missing_layout)
        self.analysis_layout.addWidget(missing_frame)
        
        # Numeric Statistics
        stats_data = statistics.get('statistics_data', {})
        numeric_stats = {k: v for k, v in stats_data.items() if isinstance(v, dict) and 'mean' in v}
        
        if numeric_stats:
            numeric_frame = QFrame()
            numeric_frame.setFrameStyle(QFrame.StyledPanel)
            numeric_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 10px;")
            numeric_layout = QVBoxLayout()
            
            numeric_title = QLabel("Numeric Columns Summary")
            numeric_title.setFont(QFont("Arial", 14, QFont.Bold))
            numeric_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
            numeric_layout.addWidget(numeric_title)
            
            # Create table for numeric statistics
            numeric_table = QTableWidget()
            numeric_table.setColumnCount(5)
            numeric_table.setHorizontalHeaderLabels(["Column", "Mean", "Std Dev", "Min", "Max"])
            numeric_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            numeric_table.setRowCount(len(numeric_stats))
            
            for row, (col_name, stats) in enumerate(numeric_stats.items()):
                numeric_table.setItem(row, 0, QTableWidgetItem(col_name))
                numeric_table.setItem(row, 1, QTableWidgetItem(f"{stats.get('mean', 0):.2f}"))
                numeric_table.setItem(row, 2, QTableWidgetItem(f"{stats.get('std', 0):.2f}"))
                numeric_table.setItem(row, 3, QTableWidgetItem(f"{stats.get('min', 0):.2f}"))
                numeric_table.setItem(row, 4, QTableWidgetItem(f"{stats.get('max', 0):.2f}"))
            
            numeric_table.setMaximumHeight(200)
            numeric_layout.addWidget(numeric_table)
            
            numeric_frame.setLayout(numeric_layout)
            self.analysis_layout.addWidget(numeric_frame)

class CompleteDatasetAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.access_token = None
        self.current_user = None
        self.current_datasets = []
        self.workers = []  # Keep track of workers for cleanup
        self.init_ui()
    
    def closeEvent(self, event):
        """Handle application close event"""
        try:
            # Clean up any running workers
            for worker in self.workers:
                if worker and worker.isRunning():
                    worker.terminate()
                    worker.wait(1000)  # Wait up to 1 second
            
            event.accept()
        except Exception as e:
            print(f"Error during cleanup: {e}")
            event.accept()
    
    def init_ui(self):
        self.setWindowTitle("Dataset Analyzer - Complete Version (No Matplotlib)")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create all tabs
        self.create_login_tab()
        self.create_dashboard_tab()
        self.create_upload_tab()
        self.create_analysis_tab()
        self.create_history_tab()
        
        # Initially disable tabs except login
        for i in range(1, 5):
            self.tabs.setTabEnabled(i, False)
    
    def create_login_tab(self):
        """Create enhanced login tab"""
        login_widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #34495e; color: white; padding: 20px;")
        header_layout = QVBoxLayout()
        
        title = QLabel("Dataset Analyzer")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white; margin: 10px;")
        
        subtitle = QLabel("Professional Desktop Application (Fixed Version)")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #bdc3c7; margin-bottom: 10px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        # Login form
        form_widget = QWidget()
        form_layout = QVBoxLayout()
        
        # Form fields
        fields_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setStyleSheet("padding: 10px; font-size: 14px; border: 2px solid #ddd; border-radius: 5px;")
        fields_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setStyleSheet("padding: 10px; font-size: 14px; border: 2px solid #ddd; border-radius: 5px;")
        fields_layout.addRow("Password:", self.password_input)
        
        form_layout.addLayout(fields_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.handle_register)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover { background-color: #229954; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.register_btn)
        form_layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("Connect to Django backend for full functionality")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; margin: 20px; font-size: 14px;")
        form_layout.addWidget(self.status_label)
        
        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)
        layout.addStretch()
        
        login_widget.setLayout(layout)
        self.tabs.addTab(login_widget, "Login")
    
    def create_dashboard_tab(self):
        """Create enhanced dashboard with statistics"""
        dashboard_widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        
        self.welcome_label = QLabel("Welcome!")
        self.welcome_label.setFont(QFont("Arial", 16))
        self.welcome_label.setStyleSheet("color: #27ae60; margin: 20px;")
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_dashboard)
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
        
        header_layout.addWidget(title)
        header_layout.addWidget(self.welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)
        
        # Statistics cards
        self.stats_frame = QFrame()
        self.stats_layout = QHBoxLayout()
        self.stats_frame.setLayout(self.stats_layout)
        layout.addWidget(self.stats_frame)
        
        # Recent datasets table
        recent_label = QLabel("Recent Datasets")
        recent_label.setFont(QFont("Arial", 18, QFont.Bold))
        recent_label.setStyleSheet("color: #2c3e50; margin: 20px 0 10px 0;")
        layout.addWidget(recent_label)
        
        self.dashboard_table = QTableWidget()
        self.dashboard_table.setColumnCount(5)
        self.dashboard_table.setHorizontalHeaderLabels(["Name", "File", "Rows", "Columns", "Upload Date"])
        self.dashboard_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.dashboard_table)
        
        dashboard_widget.setLayout(layout)
        self.tabs.addTab(dashboard_widget, "Dashboard")
    
    def create_upload_tab(self):
        """Create enhanced upload tab"""
        upload_widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Upload CSV Dataset")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        layout.addWidget(title)
        
        # Upload area
        upload_frame = QFrame()
        upload_frame.setFrameStyle(QFrame.StyledPanel)
        upload_frame.setStyleSheet("""
            QFrame {
                border: 2px dashed #bdc3c7;
                border-radius: 10px;
                background-color: #f8f9fa;
                padding: 40px;
                margin: 20px;
            }
        """)
        
        upload_layout = QVBoxLayout()
        
        # File selection
        file_layout = QVBoxLayout()
        file_layout.setAlignment(Qt.AlignCenter)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setFont(QFont("Arial", 16))
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setStyleSheet("color: #7f8c8d; margin: 20px;")
        
        select_btn = QPushButton("Select CSV File")
        select_btn.clicked.connect(self.select_file)
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(select_btn)
        upload_layout.addLayout(file_layout)
        
        upload_frame.setLayout(upload_layout)
        layout.addWidget(upload_frame)
        
        # Dataset details
        details_layout = QFormLayout()
        
        self.dataset_name = QLineEdit()
        self.dataset_name.setPlaceholderText("Enter dataset name (optional)")
        self.dataset_name.setStyleSheet("padding: 10px; font-size: 14px; border: 2px solid #ddd; border-radius: 5px;")
        details_layout.addRow("Dataset Name:", self.dataset_name)
        
        self.dataset_description = QTextEdit()
        self.dataset_description.setPlaceholderText("Enter dataset description (optional)")
        self.dataset_description.setMaximumHeight(100)
        self.dataset_description.setStyleSheet("padding: 10px; font-size: 14px; border: 2px solid #ddd; border-radius: 5px;")
        details_layout.addRow("Description:", self.dataset_description)
        
        layout.addLayout(details_layout)
        
        # Upload button
        self.upload_btn = QPushButton("Upload Dataset")
        self.upload_btn.clicked.connect(self.upload_file)
        self.upload_btn.setEnabled(False)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 18px;
                margin: 20px;
            }
            QPushButton:hover { background-color: #229954; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        layout.addWidget(self.upload_btn)
        
        layout.addStretch()
        upload_widget.setLayout(layout)
        self.tabs.addTab(upload_widget, "Upload")
        
        self.selected_file = None
    
    def create_analysis_tab(self):
        """Create data analysis tab without matplotlib"""
        analysis_widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Data Analysis & Statistics")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        header_layout.addWidget(title)
        
        # Dataset selector
        self.dataset_selector = QPushButton("Select Dataset")
        self.dataset_selector.clicked.connect(self.show_dataset_selector)
        self.dataset_selector.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(self.dataset_selector)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Splitter for dataset info and analysis
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Dataset info
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        
        info_title = QLabel("Dataset Information")
        info_title.setFont(QFont("Arial", 16, QFont.Bold))
        info_title.setStyleSheet("color: #2c3e50; margin: 10px;")
        info_layout.addWidget(info_title)
        
        self.dataset_info = QTextEdit()
        self.dataset_info.setReadOnly(True)
        self.dataset_info.setMaximumWidth(400)
        self.dataset_info.setStyleSheet("background-color: #f8f9fa; border: 1px solid #ddd; padding: 10px;")
        info_layout.addWidget(self.dataset_info)
        
        info_widget.setLayout(info_layout)
        splitter.addWidget(info_widget)
        
        # Right: Analysis display
        self.analysis_widget = DataAnalysisWidget()
        splitter.addWidget(self.analysis_widget)
        
        splitter.setSizes([400, 1000])
        layout.addWidget(splitter)
        
        analysis_widget.setLayout(layout)
        self.tabs.addTab(analysis_widget, "Analysis")
    
    def create_history_tab(self):
        """Create dataset history tab"""
        history_widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Dataset History")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        header_layout.addWidget(title)
        
        refresh_history_btn = QPushButton("Refresh History")
        refresh_history_btn.clicked.connect(self.load_history)
        refresh_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(refresh_history_btn)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["Name", "File", "Size", "Rows", "Columns", "Upload Date"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.history_table)
        
        # Pagination
        pagination_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setEnabled(False)
        
        self.page_label = QLabel("Page 1")
        self.page_label.setAlignment(Qt.AlignCenter)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.next_btn)
        
        layout.addLayout(pagination_layout)
        
        history_widget.setLayout(layout)
        self.tabs.addTab(history_widget, "History")
        
        self.current_page = 1
        self.total_pages = 1
    
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
        
        self.auth_worker = AuthWorker(username, password, 'login')
        self.workers.append(self.auth_worker)
        self.auth_worker.finished.connect(self.on_auth_finished)
        self.auth_worker.start()
    
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
        
        self.auth_worker = AuthWorker(username, password, 'register')
        self.workers.append(self.auth_worker)
        self.auth_worker.finished.connect(self.on_auth_finished)
        self.auth_worker.start()
    
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
            
            # Enable all tabs
            for i in range(1, 5):
                self.tabs.setTabEnabled(i, True)
            
            self.tabs.setCurrentIndex(1)  # Switch to dashboard
            self.refresh_dashboard()
            
        else:
            error = result.get('error', 'Unknown error')
            self.status_label.setText(f"Authentication failed: {error}")
            QMessageBox.critical(self, "Authentication Failed", f"Error: {error}")
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        if not self.access_token:
            return
        
        self.data_worker = DataWorker(self.access_token, 'load_datasets')
        self.workers.append(self.data_worker)
        self.data_worker.finished.connect(self.on_dashboard_data_loaded)
        self.data_worker.start()
    
    def on_dashboard_data_loaded(self, result):
        """Handle dashboard data loading"""
        if result['success']:
            data = result['data']
            datasets = data.get('results', [])
            self.current_datasets = datasets
            
            # Update statistics cards
            self.update_stats_cards(datasets)
            
            # Update recent datasets table
            recent_datasets = datasets[:5]  # Show last 5
            self.dashboard_table.setRowCount(len(recent_datasets))
            
            for row, dataset in enumerate(recent_datasets):
                self.dashboard_table.setItem(row, 0, QTableWidgetItem(dataset.get('name', 'Unnamed')))
                self.dashboard_table.setItem(row, 1, QTableWidgetItem(dataset.get('file_name', '')))
                self.dashboard_table.setItem(row, 2, QTableWidgetItem(str(dataset.get('total_rows', 0))))
                self.dashboard_table.setItem(row, 3, QTableWidgetItem(str(dataset.get('total_columns', 0))))
                self.dashboard_table.setItem(row, 4, QTableWidgetItem(dataset.get('upload_date', '')[:10]))
    
    def update_stats_cards(self, datasets):
        """Update statistics cards"""
        # Clear existing cards
        for i in reversed(range(self.stats_layout.count())):
            self.stats_layout.itemAt(i).widget().setParent(None)
        
        # Calculate statistics
        total_datasets = len(datasets)
        processed_datasets = len([d for d in datasets if d.get('is_processed')])
        total_rows = sum(d.get('total_rows', 0) for d in datasets)
        avg_columns = sum(d.get('total_columns', 0) for d in datasets) // total_datasets if total_datasets > 0 else 0
        
        # Create stat cards
        colors = ["#3498db", "#27ae60", "#e74c3c", "#f39c12"]
        stats = [
            ("Total Datasets", total_datasets),
            ("Processed", processed_datasets),
            ("Total Rows", f"{total_rows:,}"),
            ("Avg Columns", avg_columns)
        ]
        
        for (title, value), color in zip(stats, colors):
            card = StatCard(title, value, color)
            self.stats_layout.addWidget(card)
    
    def select_file(self):
        """Select CSV file for upload"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            self.file_label.setText(f"{filename} ({file_size:.2f} MB)")
            self.upload_btn.setEnabled(True)
            
            # Auto-fill dataset name
            if not self.dataset_name.text():
                name = os.path.splitext(filename)[0]
                self.dataset_name.setText(name)
    
    def upload_file(self):
        """Upload selected file"""
        if not self.selected_file or not self.access_token:
            return
        
        try:
            self.upload_btn.setEnabled(False)
            self.upload_btn.setText("Uploading...")
            
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            with open(self.selected_file, 'rb') as f:
                files = {'file': f}
                data = {
                    'name': self.dataset_name.text() or 'Uploaded Dataset',
                    'description': self.dataset_description.toPlainText()
                }
                
                response = requests.post('http://localhost:8000/api/datasets/upload/', 
                                       headers=headers, files=files, data=data, timeout=60)
            
            if response.status_code in [200, 201]:
                QMessageBox.information(self, "Success", "Dataset uploaded successfully!")
                
                # Clear form
                self.selected_file = None
                self.file_label.setText("No file selected")
                self.dataset_name.clear()
                self.dataset_description.clear()
                self.upload_btn.setEnabled(False)
                
                # Refresh dashboard
                self.refresh_dashboard()
            else:
                QMessageBox.critical(self, "Upload Failed", f"HTTP {response.status_code}")
                
        except Exception as e:
            QMessageBox.critical(self, "Upload Error", str(e))
        finally:
            self.upload_btn.setEnabled(True)
            self.upload_btn.setText("Upload Dataset")
    
    def show_dataset_selector(self):
        """Show dataset selection dialog"""
        if not self.current_datasets:
            QMessageBox.information(self, "No Datasets", "No datasets available. Please upload a dataset first.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Dataset for Analysis")
        dialog.setGeometry(300, 300, 400, 300)
        
        layout = QVBoxLayout()
        
        list_widget = QListWidget()
        for dataset in self.current_datasets:
            list_widget.addItem(f"{dataset.get('name', 'Unnamed')} ({dataset.get('file_name', '')})")
        
        layout.addWidget(list_widget)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            selected_row = list_widget.currentRow()
            if selected_row >= 0:
                dataset = self.current_datasets[selected_row]
                self.load_dataset_analysis(dataset)
    
    def load_dataset_analysis(self, dataset):
        """Load dataset analysis"""
        dataset_id = dataset['id']
        
        # Load dataset details
        self.data_worker = DataWorker(self.access_token, 'load_dataset_detail', dataset_id=dataset_id)
        self.data_worker.finished.connect(lambda result: self.on_dataset_detail_loaded(result, dataset_id))
        self.data_worker.start()
    
    def on_dataset_detail_loaded(self, result, dataset_id):
        """Handle dataset detail loading"""
        if result['success']:
            dataset = result['data']
            
            # Update dataset info
            info_text = f"""
Dataset: {dataset.get('name', 'Unnamed')}
File: {dataset.get('file_name', '')}
Description: {dataset.get('description', 'No description')}

Rows: {dataset.get('total_rows', 0):,}
Columns: {dataset.get('total_columns', 0)}
File Size: {dataset.get('file_size', 0) / (1024*1024):.2f} MB
Upload Date: {dataset.get('upload_date', '')}
Status: {'Processed' if dataset.get('is_processed') else 'Processing'}

Column Names: {', '.join(dataset.get('column_names', []))}
            """
            self.dataset_info.setText(info_text)
            
            # Load statistics and columns for analysis
            if dataset.get('is_processed'):
                self.load_dataset_charts(dataset_id)
            else:
                self.analysis_widget.clear_analysis()
    
    def load_dataset_charts(self, dataset_id):
        """Load dataset analysis data"""
        # Load statistics
        self.stats_worker = DataWorker(self.access_token, 'load_statistics', dataset_id=dataset_id)
        self.stats_worker.finished.connect(lambda result: self.on_stats_loaded(result, dataset_id))
        self.stats_worker.start()
    
    def on_stats_loaded(self, result, dataset_id):
        """Handle statistics loading"""
        if result['success']:
            statistics = result['data']
            
            # Load columns
            self.columns_worker = DataWorker(self.access_token, 'load_columns', dataset_id=dataset_id)
            self.columns_worker.finished.connect(lambda result: self.on_columns_loaded(result, statistics))
            self.columns_worker.start()
    
    def on_columns_loaded(self, result, statistics):
        """Handle columns loading and create analysis display"""
        if result['success']:
            columns = result['data']
            self.analysis_widget.display_dataset_analysis(statistics, columns)
    
    def load_history(self):
        """Load dataset history"""
        if not self.access_token:
            return
        
        self.data_worker = DataWorker(self.access_token, 'load_history', page=self.current_page)
        self.data_worker.finished.connect(self.on_history_loaded)
        self.data_worker.start()
    
    def on_history_loaded(self, result):
        """Handle history data loading"""
        if result['success']:
            data = result['data']
            datasets = data.get('datasets', [])
            pagination = data.get('pagination', {})
            
            # Update pagination info
            self.current_page = pagination.get('page', 1)
            self.total_pages = pagination.get('total_pages', 1)
            self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")
            self.prev_btn.setEnabled(pagination.get('has_previous', False))
            self.next_btn.setEnabled(pagination.get('has_next', False))
            
            # Update history table
            self.history_table.setRowCount(len(datasets))
            for row, dataset in enumerate(datasets):
                self.history_table.setItem(row, 0, QTableWidgetItem(dataset.get('name', 'Unnamed')))
                self.history_table.setItem(row, 1, QTableWidgetItem(dataset.get('file_name', '')))
                
                file_size = dataset.get('file_size', 0)
                size_str = f"{file_size / (1024*1024):.2f} MB" if file_size else "N/A"
                self.history_table.setItem(row, 2, QTableWidgetItem(size_str))
                
                self.history_table.setItem(row, 3, QTableWidgetItem(str(dataset.get('total_rows', 0))))
                self.history_table.setItem(row, 4, QTableWidgetItem(str(dataset.get('total_columns', 0))))
                self.history_table.setItem(row, 5, QTableWidgetItem(dataset.get('upload_date', '')[:10]))
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_history()
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_history()

def main():
    print("=== Dataset Analyzer - Complete Version (Fixed) ===")
    print("Starting complete desktop application without matplotlib...")
    print("Features: Authentication, Upload, Analysis, Statistics, History")
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Dataset Analyzer - Complete (Fixed)")
        app.setStyle('Fusion')
        
        # Set up exception handling
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            print(f"Uncaught exception: {exc_type.__name__}: {exc_value}")
            import traceback
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = handle_exception
        
        window = CompleteDatasetAnalyzer()
        window.show()
        window.raise_()
        window.activateWindow()
        
        print("Complete application launched successfully!")
        print("Available features:")
        print("   - Professional login/register")
        print("   - Statistics dashboard with cards")
        print("   - CSV file upload with metadata")
        print("   - Text-based data analysis (no matplotlib)")
        print("   - Dataset statistics and visualization")
        print("   - Paginated dataset history")
        print("   - Fixed Qt5 backend issues")
        
        return app.exec_()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())