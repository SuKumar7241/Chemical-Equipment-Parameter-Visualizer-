"""
Dashboard tab showing overview statistics
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QGridLayout, QPushButton)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QFont

from services.dataset_service import DatasetService, DatasetException


class DashboardWorker(QThread):
    """Worker thread for loading dashboard data"""
    data_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, dataset_service):
        super().__init__()
        self.dataset_service = dataset_service
    
    def run(self):
        try:
            # Get datasets
            datasets = self.dataset_service.get_datasets()
            
            # Calculate statistics
            total_datasets = len(datasets)
            processed_datasets = len([d for d in datasets if d.get('is_processed')])
            total_rows = sum(d.get('total_rows', 0) for d in datasets)
            total_columns = sum(d.get('total_columns', 0) for d in datasets)
            avg_columns = total_columns // total_datasets if total_datasets > 0 else 0
            
            # Get recent datasets (last 5)
            recent_datasets = datasets[:5]
            
            data = {
                'stats': {
                    'total_datasets': total_datasets,
                    'processed_datasets': processed_datasets,
                    'total_rows': total_rows,
                    'avg_columns': avg_columns
                },
                'recent_datasets': recent_datasets
            }
            
            self.data_loaded.emit(data)
            
        except DatasetException as e:
            self.error_occurred.emit(str(e))


class StatCard(QFrame):
    """Widget for displaying a statistic"""
    
    def __init__(self, title, value, color="#3498db"):
        super().__init__()
        self.init_ui(title, value, color)
    
    def init_ui(self, title, value, color):
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid {color};
                border-radius: 12px;
                padding: 20px;
                margin: 5px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 3px solid {color};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Arial", 32, QFont.Bold))
        value_label.setStyleSheet(f"""
            color: {color};
            font-weight: 700;
            margin: 10px 0;
        """)
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("""
            color: #6c757d;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 5px 0;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        self.setLayout(layout)
        self.setFixedHeight(150)
        self.setMinimumWidth(200)


class DashboardTab(QWidget):
    def __init__(self, dataset_service: DatasetService):
        super().__init__()
        self.dataset_service = dataset_service
        self.worker = None
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        layout.addWidget(title)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                margin-bottom: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(refresh_btn)
        
        # Stats grid
        self.stats_frame = QFrame()
        self.stats_layout = QGridLayout()
        self.stats_frame.setLayout(self.stats_layout)
        layout.addWidget(self.stats_frame)
        
        # Recent datasets section
        recent_label = QLabel("Recent Datasets")
        recent_label.setFont(QFont("Arial", 16, QFont.Bold))
        recent_label.setStyleSheet("color: #2c3e50; margin: 20px 0 10px 0;")
        layout.addWidget(recent_label)
        
        # Recent datasets list
        self.recent_scroll = QScrollArea()
        self.recent_widget = QWidget()
        self.recent_layout = QVBoxLayout()
        self.recent_widget.setLayout(self.recent_layout)
        self.recent_scroll.setWidget(self.recent_widget)
        self.recent_scroll.setWidgetResizable(True)
        self.recent_scroll.setMaximumHeight(300)
        layout.addWidget(self.recent_scroll)
        
        # Loading label
        self.loading_label = QLabel("Loading...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        layout.addWidget(self.loading_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def load_data(self):
        """Load dashboard data in background thread"""
        if self.worker and self.worker.isRunning():
            return
        
        self.loading_label.setText("Loading...")
        self.loading_label.show()
        
        self.worker = DashboardWorker(self.dataset_service)
        self.worker.data_loaded.connect(self.on_data_loaded)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()
    
    @pyqtSlot(dict)
    def on_data_loaded(self, data):
        """Handle loaded data"""
        self.loading_label.hide()
        
        # Clear existing stats
        for i in reversed(range(self.stats_layout.count())):
            self.stats_layout.itemAt(i).widget().setParent(None)
        
        # Add stat cards
        stats = data['stats']
        colors = ["#007bff", "#28a745", "#dc3545", "#ffc107"]  # Blue, Green, Red, Yellow
        
        stat_items = [
            ("Total Datasets", stats['total_datasets']),
            ("Processed", stats['processed_datasets']),
            ("Total Rows", f"{stats['total_rows']:,}"),
            ("Avg Columns", stats['avg_columns'])
        ]
        
        for i, (title, value) in enumerate(stat_items):
            card = StatCard(title, value, colors[i % len(colors)])
            self.stats_layout.addWidget(card, i // 2, i % 2)
        
        # Update recent datasets
        self.update_recent_datasets(data['recent_datasets'])
    
    def update_recent_datasets(self, datasets):
        """Update recent datasets list"""
        # Clear existing items
        for i in reversed(range(self.recent_layout.count())):
            self.recent_layout.itemAt(i).widget().setParent(None)
        
        if not datasets:
            no_data = QLabel("No datasets found")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("color: #7f8c8d; font-style: italic;")
            self.recent_layout.addWidget(no_data)
            return
        
        for dataset in datasets:
            item = self.create_dataset_item(dataset)
            self.recent_layout.addWidget(item)
    
    def create_dataset_item(self, dataset):
        """Create a dataset item widget"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                margin: 2px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Dataset info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(dataset.get('name', 'Unnamed'))
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(name_label)
        
        details = []
        if dataset.get('file_name'):
            details.append(f"File: {dataset['file_name']}")
        if dataset.get('total_rows'):
            details.append(f"Rows: {dataset['total_rows']:,}")
        if dataset.get('total_columns'):
            details.append(f"Columns: {dataset['total_columns']}")
        
        details_label = QLabel(" | ".join(details))
        details_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        info_layout.addWidget(details_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Status
        status = "Processed" if dataset.get('is_processed') else "Processing"
        status_color = "#27ae60" if dataset.get('is_processed') else "#f39c12"
        
        status_label = QLabel(status)
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        layout.addWidget(status_label)
        
        frame.setLayout(layout)
        return frame
    
    @pyqtSlot(str)
    def on_error(self, error_msg):
        """Handle error"""
        self.loading_label.setText(f"Error: {error_msg}")
    
    def refresh_data(self):
        """Refresh dashboard data"""
        self.load_data()