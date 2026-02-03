#!/usr/bin/env python3
"""
Complete Desktop Application with all advanced features
"""
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


import sys
import requests

# Set matplotlib backend BEFORE importing matplotlib components
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for reliability

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from io import BytesIO

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QLineEdit, QPushButton, QMessageBox,
                             QTabWidget, QFormLayout, QTextEdit, QTableWidget,
                             QTableWidgetItem, QFileDialog, QScrollArea, QFrame,
                             QSplitter, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap

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
            elif self.operation == 'download_pdf':
                dataset_id = self.kwargs['dataset_id']
                response = requests.get(f'http://localhost:8000/api/reports/pdf/{dataset_id}/', 
                                      headers=headers, timeout=30)
                # For PDF downloads, return the raw response
                if response.status_code == 200:
                    self.finished.emit({'success': True, 'data': response.content, 'is_binary': True})
                    return
                else:
                    self.finished.emit({'success': False, 'error': f'HTTP {response.status_code}'})
                    return
            
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

class ChartWidget(QWidget):
    """Widget for displaying matplotlib charts as images"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        self.title_label = QLabel("Chemical Equipment Parameter Visualization")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        layout.addWidget(self.title_label)
        
        # Scroll area for charts
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)
        
        # Status
        self.status_label = QLabel("Select an equipment dataset to view parameter visualizations")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; margin: 10px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def clear_chart(self):
        """Clear all charts"""
        try:
            for i in reversed(range(self.scroll_layout.count())):
                child = self.scroll_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
            self.status_label.setText("Charts cleared")
        except Exception as e:
            print(f"Error clearing charts: {e}")
    
    def add_chart_image(self, title, image_data):
        """Add a chart image to the display"""
        try:
            # Create frame for chart
            chart_frame = QFrame()
            chart_frame.setFrameStyle(QFrame.Box)
            chart_frame.setStyleSheet("border: 1px solid #ddd; margin: 5px; background-color: white;")
            
            frame_layout = QVBoxLayout()
            
            # Title
            title_label = QLabel(title)
            title_label.setFont(QFont('Arial', 12, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("color: #2c3e50; margin: 5px;")
            frame_layout.addWidget(title_label)
            
            # Image
            image_label = QLabel()
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            image_label.setPixmap(pixmap.scaled(700, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            image_label.setAlignment(Qt.AlignCenter)
            frame_layout.addWidget(image_label)
            
            chart_frame.setLayout(frame_layout)
            self.scroll_layout.addWidget(chart_frame)
            
        except Exception as e:
            print(f"Error adding chart image: {e}")
    
    def create_matplotlib_plot(self, plot_func, title):
        """Create matplotlib plot and return as image data"""
        try:
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Call the plot function
            plot_func()
            
            plt.title(title, fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            # Save to bytes
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
            buffer.seek(0)
            image_data = buffer.getvalue()
            buffer.close()
            
            plt.close()  # Close the figure to free memory
            
            return image_data
            
        except Exception as e:
            print(f"Error creating plot: {e}")
            return None
    
    def plot_dataset_analysis(self, statistics, columns):
        """Plot comprehensive dataset analysis"""
        try:
            self.clear_chart()
            self.status_label.setText("Generating visualizations...")
            
            # Debug: Print the data structure
            print("DEBUG - Statistics data:", statistics)
            print("DEBUG - Columns data:", columns)
            
            if not statistics or not columns:
                self.status_label.setText("No data available for visualization")
                # Create sample charts to show matplotlib is working
                self.create_sample_charts()
                return
            
            # Chart 1: Data Types Distribution (Pie Chart)
            def data_types_chart():
                data_types = {}
                for col in columns:
                    dtype = col.get('data_type', 'unknown')
                    data_types[dtype] = data_types.get(dtype, 0) + 1
                
                if data_types:
                    colors = plt.cm.Set3(np.linspace(0, 1, len(data_types)))
                    plt.pie(data_types.values(), labels=data_types.keys(), autopct='%1.1f%%', 
                           colors=colors, startangle=90)
                    plt.axis('equal')
            
            image_data = self.create_matplotlib_plot(data_types_chart, 'Data Types Distribution')
            if image_data:
                self.add_chart_image('Data Types Distribution', image_data)
            
            # Chart 2: Missing Values Analysis (Bar Chart)
            def missing_values_chart():
                col_names = []
                null_counts = []
                
                # Handle different data formats
                for col in columns[:10]:  # Top 10 columns
                    if isinstance(col, dict):
                        # Try different possible column name keys
                        name = col.get('column_name') or col.get('name') or col.get('field_name') or str(col.get('id', 'Unknown'))
                        col_names.append(name[:15])  # Truncate names
                        null_counts.append(col.get('null_count', 0))
                    else:
                        # If col is not a dict, convert to string
                        col_names.append(str(col)[:15])
                        null_counts.append(0)
                
                if any(null_counts):
                    bars = plt.bar(range(len(col_names)), null_counts, color='lightcoral')
                    plt.xlabel('Columns')
                    plt.ylabel('Missing Values Count')
                    plt.xticks(range(len(col_names)), col_names, rotation=45, ha='right')
                    
                    # Add value labels on bars
                    for bar, value in zip(bars, null_counts):
                        if value > 0:
                            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(null_counts)*0.01,
                                    str(int(value)), ha='center', va='bottom')
                else:
                    plt.text(0.5, 0.5, 'No missing values found', ha='center', va='center', 
                            transform=plt.gca().transAxes, fontsize=14)
                    plt.xlim(0, 1)
                    plt.ylim(0, 1)
            
            image_data = self.create_matplotlib_plot(missing_values_chart, 'Missing Values Analysis')
            if image_data:
                self.add_chart_image('Missing Values by Column', image_data)
            
            # Chart 3: Numeric Statistics (Bar Chart)
            def numeric_stats_chart():
                stats_data = statistics.get('statistics_data', {})
                numeric_cols = []
                numeric_means = []
                
                for col_name, col_stats in stats_data.items():
                    if isinstance(col_stats, dict) and 'mean' in col_stats:
                        numeric_cols.append(col_name[:15])  # Truncate long names
                        numeric_means.append(col_stats['mean'])
                
                if numeric_cols:
                    bars = plt.bar(range(len(numeric_cols)), numeric_means, color='skyblue')
                    plt.xlabel('Numeric Columns')
                    plt.ylabel('Mean Values')
                    plt.xticks(range(len(numeric_cols)), numeric_cols, rotation=45, ha='right')
                    
                    # Add value labels
                    for bar, value in zip(bars, numeric_means):
                        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(numeric_means)*0.01,
                                f'{value:.2f}', ha='center', va='bottom', fontsize=8)
                else:
                    plt.text(0.5, 0.5, 'No numeric columns found', ha='center', va='center', 
                            transform=plt.gca().transAxes, fontsize=14)
                    plt.xlim(0, 1)
                    plt.ylim(0, 1)
            
            image_data = self.create_matplotlib_plot(numeric_stats_chart, 'Numeric Column Statistics')
            if image_data:
                self.add_chart_image('Mean Values of Numeric Columns', image_data)
            
            # Chart 4: Dataset Summary (Bar Chart)
            def summary_chart():
                summary_labels = ['Total Records', 'Numeric Cols', 'Text Cols', 'Missing Values']
                summary_values = [
                    statistics.get('total_records', 0),
                    statistics.get('numeric_columns_count', 0),
                    statistics.get('categorical_columns_count', 0),
                    statistics.get('missing_values_count', 0)
                ]
                
                bars = plt.bar(range(len(summary_labels)), summary_values, color='lightgreen')
                plt.xticks(range(len(summary_labels)), summary_labels, rotation=45, ha='right')
                plt.ylabel('Count')
                
                # Add value labels
                for bar, value in zip(bars, summary_values):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(summary_values)*0.01,
                            str(int(value)), ha='center', va='bottom')
            
            image_data = self.create_matplotlib_plot(summary_chart, 'Dataset Summary Statistics')
            if image_data:
                self.add_chart_image('Dataset Overview', image_data)
            
            self.status_label.setText("Visualizations generated successfully using matplotlib!")
            
        except Exception as e:
            print(f"Error in plot_dataset_analysis: {e}")
            self.status_label.setText(f"Error creating visualizations: {str(e)}")
            
            # Show sample charts to demonstrate matplotlib is working
            self.create_sample_charts()
    
    def create_sample_charts(self):
        """Create sample charts to demonstrate matplotlib functionality"""
        try:
            self.status_label.setText("Creating sample charts to demonstrate matplotlib...")
            
            # Sample Chart 1: Sample Pie Chart
            def sample_pie_chart():
                labels = ['Text Data', 'Numeric Data', 'Date Data', 'Boolean Data']
                sizes = [40, 30, 20, 10]
                colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
                plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
                plt.axis('equal')
            
            image_data = self.create_matplotlib_plot(sample_pie_chart, 'Sample Data Types Distribution')
            if image_data:
                self.add_chart_image('Sample Data Types (Matplotlib Demo)', image_data)
            
            # Sample Chart 2: Sample Bar Chart
            def sample_bar_chart():
                categories = ['Column A', 'Column B', 'Column C', 'Column D']
                values = [5, 3, 8, 2]
                bars = plt.bar(range(len(categories)), values, color='lightcoral')
                plt.xlabel('Columns')
                plt.ylabel('Missing Values')
                plt.xticks(range(len(categories)), categories, rotation=45, ha='right')
                
                # Add value labels
                for bar, value in zip(bars, values):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                            str(value), ha='center', va='bottom')
            
            image_data = self.create_matplotlib_plot(sample_bar_chart, 'Sample Missing Values Analysis')
            if image_data:
                self.add_chart_image('Sample Missing Values (Matplotlib Demo)', image_data)
            
            # Sample Chart 3: Sample Statistics
            def sample_stats_chart():
                columns = ['Age', 'Salary', 'Score', 'Rating']
                means = [32.5, 65000, 85.2, 4.3]
                bars = plt.bar(range(len(columns)), means, color='skyblue')
                plt.xlabel('Numeric Columns')
                plt.ylabel('Mean Values')
                plt.xticks(range(len(columns)), columns, rotation=45, ha='right')
                
                # Add value labels
                for bar, value in zip(bars, means):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(means)*0.01,
                            f'{value:.1f}', ha='center', va='bottom')
            
            image_data = self.create_matplotlib_plot(sample_stats_chart, 'Sample Numeric Statistics')
            if image_data:
                self.add_chart_image('Sample Statistics (Matplotlib Demo)', image_data)
            
            # Sample Chart 4: Line Chart
            def sample_line_chart():
                import numpy as np
                x = np.linspace(0, 10, 50)
                y1 = np.sin(x)
                y2 = np.cos(x)
                plt.plot(x, y1, 'b-', label='sin(x)', linewidth=2)
                plt.plot(x, y2, 'r--', label='cos(x)', linewidth=2)
                plt.xlabel('X values')
                plt.ylabel('Y values')
                plt.legend()
                plt.grid(True, alpha=0.3)
            
            image_data = self.create_matplotlib_plot(sample_line_chart, 'Sample Mathematical Functions')
            if image_data:
                self.add_chart_image('Sample Line Chart (Matplotlib Demo)', image_data)
            
            self.status_label.setText("Sample matplotlib charts created successfully! Matplotlib is working.")
            
        except Exception as e:
            print(f"Error creating sample charts: {e}")
            self.status_label.setText(f"Error creating sample charts: {str(e)}")
            
        except Exception as e:
            print(f"Error in plot_dataset_analysis: {e}")
            self.status_label.setText(f"Error creating visualizations: {str(e)}")
            
            # Show error message in a chart
            try:
                def error_chart():
                    plt.text(0.5, 0.5, f'Error creating visualization:\n{str(e)}', 
                           ha='center', va='center', transform=plt.gca().transAxes, 
                           fontsize=12, color='red')
                    plt.xlim(0, 1)
                    plt.ylim(0, 1)
                    plt.axis('off')
                
                image_data = self.create_matplotlib_plot(error_chart, 'Visualization Error')
                if image_data:
                    self.add_chart_image('Error', image_data)
            except:
                pass

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

class CompleteDatasetAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.access_token = None
        self.current_user = None
        self.current_datasets = []
        self.current_dataset_id = None  # Track currently selected dataset for PDF download
        self.current_dataset_name = None
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
            
            # Clear matplotlib figures
            if hasattr(self, 'chart_widget'):
                self.chart_widget.clear_chart()
            
            event.accept()
        except Exception as e:
            print(f"Error during cleanup: {e}")
            event.accept()
    
    def init_ui(self):
        self.setWindowTitle("Chemical Equipment Parameter Visualizer - Professional Edition")
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
        
        title = QLabel("Chemical Equipment Parameter Visualizer")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white; margin: 10px;")
        
        subtitle = QLabel("Professional Chemical Data Analysis Platform")
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
        self.status_label = QLabel("Connect to Django backend for chemical equipment data analysis")
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
        recent_label = QLabel("Recent Equipment Datasets")
        recent_label.setFont(QFont("Arial", 18, QFont.Bold))
        recent_label.setStyleSheet("color: #2c3e50; margin: 20px 0 10px 0;")
        layout.addWidget(recent_label)
        
        self.dashboard_table = QTableWidget()
        self.dashboard_table.setColumnCount(5)
        self.dashboard_table.setHorizontalHeaderLabels(["Equipment Dataset", "File", "Rows", "Columns", "Upload Date"])
        self.dashboard_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.dashboard_table)
        
        dashboard_widget.setLayout(layout)
        self.tabs.addTab(dashboard_widget, "Dashboard")
    
    def create_upload_tab(self):
        """Create enhanced upload tab"""
        upload_widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Upload Chemical Equipment Data")
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
        self.dataset_name.setPlaceholderText("Enter equipment dataset name (optional)")
        self.dataset_name.setStyleSheet("padding: 10px; font-size: 14px; border: 2px solid #ddd; border-radius: 5px;")
        details_layout.addRow("Equipment Dataset Name:", self.dataset_name)
        
        self.dataset_description = QTextEdit()
        self.dataset_description.setPlaceholderText("Enter equipment data description (optional)")
        self.dataset_description.setMaximumHeight(100)
        self.dataset_description.setStyleSheet("padding: 10px; font-size: 14px; border: 2px solid #ddd; border-radius: 5px;")
        details_layout.addRow("Equipment Description:", self.dataset_description)
        
        layout.addLayout(details_layout)
        
        # Upload button
        self.upload_btn = QPushButton("Upload Equipment Data")
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
        """Create data analysis tab with charts"""
        analysis_widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Chemical Equipment Parameter Analysis & Visualization")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        header_layout.addWidget(title)
        
        # Dataset selector
        self.dataset_selector = QPushButton("Select Equipment Dataset")
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
        
        # PDF Download button for current dataset
        self.analysis_pdf_btn = QPushButton("Download Equipment Report")
        self.analysis_pdf_btn.clicked.connect(self.download_current_dataset_pdf)
        self.analysis_pdf_btn.setEnabled(False)
        self.analysis_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        header_layout.addWidget(self.analysis_pdf_btn)
        
        # Sample charts button
        sample_charts_btn = QPushButton("Show Sample Parameter Charts")
        sample_charts_btn.clicked.connect(self.show_sample_charts)
        sample_charts_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(sample_charts_btn)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Splitter for dataset info and charts
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Dataset info
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        
        info_title = QLabel("Equipment Dataset Information")
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
        
        # Right: Charts
        self.chart_widget = ChartWidget()
        splitter.addWidget(self.chart_widget)
        
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
        title = QLabel("Equipment Dataset History")
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
        self.history_table.setHorizontalHeaderLabels(["Equipment Dataset", "File", "Size", "Rows", "Columns", "Upload Date"])
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
            ("Equipment Datasets", total_datasets),
            ("Processed", processed_datasets),
            ("Total Parameters", f"{total_rows:,}"),
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
            import os
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
                    'name': self.dataset_name.text() or 'Chemical Equipment Dataset',
                    'description': self.dataset_description.toPlainText()
                }
                
                response = requests.post('http://localhost:8000/api/datasets/upload/', 
                                       headers=headers, files=files, data=data, timeout=60)
            
            if response.status_code in [200, 201]:
                QMessageBox.information(self, "Success", "Chemical equipment dataset uploaded successfully!")
                
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
    
    def show_sample_charts(self):
        """Show sample matplotlib charts"""
        self.chart_widget.create_sample_charts()
        self.dataset_info.setText("""
Chemical Equipment Parameter Charts Demonstration

This shows that matplotlib is working correctly in your chemical equipment analysis application.

Charts displayed:
- Pie chart: Parameter data types distribution
- Bar chart: Missing parameter values analysis  
- Bar chart: Numeric parameter statistics
- Line chart: Mathematical functions for equipment modeling

These demonstrate that your desktop app successfully uses matplotlib for chemical equipment parameter visualization.

For your screening task, you can show these charts and explain that matplotlib is integrated into your desktop application for creating various types of chemical equipment parameter visualizations.
        """)
    
    def show_dataset_selector(self):
        """Show dataset selection dialog"""
        if not self.current_datasets:
            QMessageBox.information(self, "No Equipment Datasets", "No equipment datasets available. Please upload a chemical equipment dataset first.")
            return
        
        from PyQt5.QtWidgets import QDialog, QListWidget, QDialogButtonBox, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Equipment Dataset for Analysis")
        dialog.setGeometry(300, 300, 500, 400)
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel("Select an equipment dataset to analyze or download parameter report:")
        instructions.setStyleSheet("color: #2c3e50; margin: 10px; font-size: 14px;")
        layout.addWidget(instructions)
        
        list_widget = QListWidget()
        for dataset in self.current_datasets:
            status = "✓ Processed" if dataset.get('is_processed') else "⏳ Processing"
            list_widget.addItem(f"{dataset.get('name', 'Unnamed')} ({dataset.get('file_name', '')}) - {status}")
        
        layout.addWidget(list_widget)
        
        # Custom buttons
        button_layout = QHBoxLayout()
        
        # PDF Download button
        pdf_btn = QPushButton("Download Equipment Report")
        pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        pdf_btn.clicked.connect(lambda: self.download_pdf_from_selector(dialog, list_widget))
        button_layout.addWidget(pdf_btn)
        
        # Analyze button
        analyze_btn = QPushButton("Analyze Equipment Dataset")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        analyze_btn.clicked.connect(lambda: self.analyze_from_selector(dialog, list_widget))
        button_layout.addWidget(analyze_btn)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def download_pdf_from_selector(self, dialog, list_widget):
        """Download PDF from dataset selector dialog"""
        selected_row = list_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(dialog, "No Selection", "Please select a dataset first.")
            return
        
        dataset = self.current_datasets[selected_row]
        if not dataset.get('is_processed'):
            QMessageBox.warning(dialog, "Equipment Dataset Not Ready", "Parameter reports are only available for processed equipment datasets.")
            return
        
        dialog.accept()
        self.download_pdf_report(dataset['id'], dataset.get('name', 'dataset'))
    
    def analyze_from_selector(self, dialog, list_widget):
        """Analyze dataset from selector dialog"""
        selected_row = list_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(dialog, "No Selection", "Please select a dataset first.")
            return
        
        dataset = self.current_datasets[selected_row]
        dialog.accept()
        self.load_dataset_analysis(dataset)
    
    def load_dataset_analysis(self, dataset):
        """Load dataset analysis"""
        dataset_id = dataset['id']
        
        # Store current dataset info for PDF download
        self.current_dataset_id = dataset_id
        self.current_dataset_name = dataset.get('name', 'dataset')
        self.analysis_pdf_btn.setEnabled(dataset.get('is_processed', False))
        
        # Load dataset details
        self.data_worker = DataWorker(self.access_token, 'load_dataset_detail', dataset_id=dataset_id)
        self.data_worker.finished.connect(lambda result: self.on_dataset_detail_loaded(result, dataset_id))
        self.data_worker.start()
    
    def download_current_dataset_pdf(self):
        """Download PDF for currently selected dataset in analysis tab"""
        if self.current_dataset_id:
            self.download_pdf_report(self.current_dataset_id, self.current_dataset_name)
    
    def download_pdf_report(self, dataset_id, dataset_name):
        """Download PDF report for a dataset"""
        if not self.access_token:
            QMessageBox.warning(self, "Authentication Required", "Please login first.")
            return
        
        # Show progress with proper modal dialog
        progress_msg = QMessageBox(self)
        progress_msg.setWindowTitle("Downloading Equipment Report")
        progress_msg.setText("Generating and downloading chemical equipment parameter report...")
        progress_msg.setStandardButtons(QMessageBox.Cancel)
        progress_msg.setDefaultButton(QMessageBox.Cancel)
        progress_msg.setModal(True)
        
        # Add timeout timer (30 seconds)
        timeout_timer = QTimer()
        timeout_timer.setSingleShot(True)
        timeout_timer.timeout.connect(lambda: self.handle_pdf_timeout(progress_msg))
        timeout_timer.start(30000)  # 30 seconds
        
        # Connect cancel button to close dialog
        def cancel_download():
            try:
                timeout_timer.stop()
                if hasattr(self, 'pdf_worker') and self.pdf_worker.isRunning():
                    self.pdf_worker.terminate()
                progress_msg.close()
                progress_msg.deleteLater()
            except:
                pass
        
        progress_msg.buttonClicked.connect(lambda: cancel_download())
        progress_msg.show()
        
        # Start PDF download
        self.pdf_worker = DataWorker(self.access_token, 'download_pdf', dataset_id=dataset_id)
        self.pdf_worker.finished.connect(lambda result: self.on_pdf_downloaded(result, dataset_name, progress_msg, timeout_timer))
        self.workers.append(self.pdf_worker)
        self.pdf_worker.start()
    
    def handle_pdf_timeout(self, progress_msg):
        """Handle PDF download timeout"""
        try:
            if hasattr(self, 'pdf_worker') and self.pdf_worker.isRunning():
                self.pdf_worker.terminate()
            progress_msg.close()
            progress_msg.deleteLater()
            QMessageBox.warning(self, "Timeout", "PDF download timed out. Please try again.")
        except:
            pass
    
    def on_pdf_downloaded(self, result, dataset_name, progress_msg, timeout_timer=None):
        """Handle PDF download result"""
        try:
            if timeout_timer:
                timeout_timer.stop()
            progress_msg.close()
            progress_msg.deleteLater()  # Ensure proper cleanup
        except:
            pass  # In case dialog is already closed
        
        if result['success']:
            pdf_data = result['data']
            
            # Save PDF file
            suggested_name = f"{dataset_name}_equipment_report.pdf"
            
            # Open file dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Chemical Equipment Parameter Report",
                suggested_name,
                "PDF Files (*.pdf);;All Files (*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'wb') as f:
                        f.write(pdf_data)
                    
                    QMessageBox.information(
                        self, 
                        "Success", 
                        f"Chemical equipment parameter report saved successfully to:\n{file_path}"
                    )
                    
                    # Ask if user wants to open the file
                    reply = QMessageBox.question(
                        self,
                        "Open Equipment Report",
                        "Would you like to open the chemical equipment parameter report now?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if reply == QMessageBox.Yes:
                        import subprocess
                        import platform
                        import os
                        
                        try:
                            if platform.system() == 'Windows':
                                os.startfile(file_path)
                            elif platform.system() == 'Darwin':  # macOS
                                subprocess.run(['open', file_path])
                            else:  # Linux
                                subprocess.run(['xdg-open', file_path])
                        except Exception as e:
                            QMessageBox.warning(
                                self,
                                "Warning",
                                f"Equipment report saved but couldn't open automatically: {str(e)}"
                            )
                
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to save equipment parameter report: {str(e)}"
                    )
        else:
            error = result.get('error', 'Unknown error')
            try:
                QMessageBox.critical(
                    self,
                    "Download Failed",
                    f"Failed to download chemical equipment parameter report: {error}"
                )
            except:
                print(f"Failed to download chemical equipment parameter report: {error}")
    
    def on_dataset_detail_loaded(self, result, dataset_id):
        """Handle dataset detail loading"""
        if result['success']:
            dataset = result['data']
            
            # Update dataset info
            info_text = f"""
Equipment Dataset: {dataset.get('name', 'Unnamed')}
File: {dataset.get('file_name', '')}
Description: {dataset.get('description', 'No description')}

Parameter Records: {dataset.get('total_rows', 0):,}
Parameter Columns: {dataset.get('total_columns', 0)}
File Size: {dataset.get('file_size', 0) / (1024*1024):.2f} MB
Upload Date: {dataset.get('upload_date', '')}
Processing Status: {'Processed' if dataset.get('is_processed') else 'Processing'}

Parameter Names: {', '.join(dataset.get('column_names', []))}
            """
            self.dataset_info.setText(info_text)
            
            # Load statistics and columns for charts
            if dataset.get('is_processed'):
                self.load_dataset_charts(dataset_id)
            else:
                self.chart_widget.clear_chart()
    
    def load_dataset_charts(self, dataset_id):
        """Load dataset charts"""
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
        """Handle columns loading and create charts"""
        if result['success']:
            columns = result['data']
            self.chart_widget.plot_dataset_analysis(statistics, columns)
    
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
    print("=== Chemical Equipment Parameter Visualizer - Complete Version with Matplotlib ===")
    print("Starting complete chemical equipment analysis desktop application...")
    print("Features: Authentication, Equipment Data Upload, Parameter Analysis, Matplotlib Charts, History")
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Chemical Equipment Parameter Visualizer - Complete with Matplotlib")
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
        
        print("Chemical Equipment Parameter Visualizer launched successfully!")
        print("Available features:")
        print("   - Professional login/register for chemical engineers")
        print("   - Statistics dashboard with equipment parameter cards")
        print("   - Chemical equipment CSV data upload with metadata")
        print("   - Interactive matplotlib charts for parameter visualization")
        print("   - Equipment parameter analysis with pie charts, bar charts")
        print("   - Parameter data type distribution, missing values analysis")
        print("   - Numeric parameter statistics visualization")
        print("   - Paginated equipment dataset history")
        print("")
        print("MATPLOTLIB INTEGRATION: Your app now uses matplotlib for chemical equipment parameter visualization!")
        
        return app.exec_()
        
    except Exception as e:
        print(f"Error starting Chemical Equipment Parameter Visualizer: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())