"""
History tab for viewing dataset history with pagination
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                             QHeaderView, QAbstractItemView, QFrame, QSpinBox)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QFont

from services.dataset_service import DatasetService, DatasetException


class HistoryWorker(QThread):
    """Worker thread for loading history data"""
    data_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, dataset_service, page=1, page_size=10):
        super().__init__()
        self.dataset_service = dataset_service
        self.page = page
        self.page_size = page_size
    
    def run(self):
        try:
            # Get history data
            history_data = self.dataset_service.get_dataset_history(self.page, self.page_size)
            
            # Get history status
            try:
                status_data = self.dataset_service.get_history_status()
                history_data['status'] = status_data
            except DatasetException:
                history_data['status'] = None
            
            self.data_loaded.emit(history_data)
            
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
                background-color: white;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Value
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Arial", 18, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setStyleSheet("color: #7f8c8d;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        self.setLayout(layout)
        self.setFixedHeight(80)


class HistoryTab(QWidget):
    dataset_deleted = pyqtSignal()
    
    def __init__(self, dataset_service: DatasetService):
        super().__init__()
        self.dataset_service = dataset_service
        self.history_worker = None
        self.current_page = 1
        self.page_size = 10
        self.total_pages = 1
        self.datasets = []
        self.init_ui()
        self.load_history()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title and refresh button
        header_layout = QHBoxLayout()
        
        title = QLabel("Dataset History")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Stats overview
        self.stats_frame = QFrame()
        self.stats_layout = QHBoxLayout()
        self.stats_frame.setLayout(self.stats_layout)
        layout.addWidget(self.stats_frame)
        
        # History table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)
        
        # Pagination controls
        pagination_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setEnabled(False)
        pagination_layout.addWidget(self.prev_btn)
        
        pagination_layout.addStretch()
        
        # Page info
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setAlignment(Qt.AlignCenter)
        pagination_layout.addWidget(self.page_label)
        
        pagination_layout.addStretch()
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        pagination_layout.addWidget(self.next_btn)
        
        layout.addLayout(pagination_layout)
        
        # Delete button
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        layout.addWidget(self.delete_btn)
        
        # Loading label
        self.loading_label = QLabel("Loading history...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(self.loading_label)
        
        self.setLayout(layout)
    
    def load_history(self):
        """Load history data in background thread"""
        if self.history_worker and self.history_worker.isRunning():
            return
        
        self.loading_label.show()
        self.table.setRowCount(0)
        
        self.history_worker = HistoryWorker(
            self.dataset_service, self.current_page, self.page_size
        )
        self.history_worker.data_loaded.connect(self.on_history_loaded)
        self.history_worker.error_occurred.connect(self.on_error)
        self.history_worker.start()
    
    @pyqtSlot(dict)
    def on_history_loaded(self, data):
        """Handle loaded history data"""
        self.loading_label.hide()
        
        # Update stats
        self.update_stats(data.get('status'))
        
        # Update pagination info
        pagination = data.get('pagination', {})
        self.current_page = pagination.get('page', 1)
        self.total_pages = pagination.get('total_pages', 1)
        
        self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")
        self.prev_btn.setEnabled(pagination.get('has_previous', False))
        self.next_btn.setEnabled(pagination.get('has_next', False))
        
        # Update table
        datasets = data.get('datasets', [])
        self.datasets = datasets
        
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Name", "File Name", "Size", "Rows", "Columns", "Upload Date", "Status", "Description"
        ])
        
        self.table.setRowCount(len(datasets))
        
        for row, dataset in enumerate(datasets):
            # Name
            name_item = QTableWidgetItem(dataset.get('name', 'Unnamed'))
            self.table.setItem(row, 0, name_item)
            
            # File name
            file_item = QTableWidgetItem(dataset.get('file_name', ''))
            self.table.setItem(row, 1, file_item)
            
            # Size
            file_size = dataset.get('file_size', 0)
            if file_size:
                size_mb = file_size / (1024 * 1024)
                size_str = f"{size_mb:.2f} MB"
            else:
                size_str = "N/A"
            size_item = QTableWidgetItem(size_str)
            self.table.setItem(row, 2, size_item)
            
            # Rows
            rows_item = QTableWidgetItem(f"{dataset.get('total_rows', 0):,}")
            self.table.setItem(row, 3, rows_item)
            
            # Columns
            cols_item = QTableWidgetItem(str(dataset.get('total_columns', 0)))
            self.table.setItem(row, 4, cols_item)
            
            # Upload date
            from datetime import datetime
            upload_date = dataset.get('upload_date', '')
            if upload_date:
                try:
                    dt = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                    date_str = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    date_str = upload_date
            else:
                date_str = ''
            date_item = QTableWidgetItem(date_str)
            self.table.setItem(row, 5, date_item)
            
            # Status
            status = "Processed" if dataset.get('is_processed') else "Processing"
            status_item = QTableWidgetItem(status)
            self.table.setItem(row, 6, status_item)
            
            # Description
            desc = dataset.get('description', '')
            if len(desc) > 50:
                desc = desc[:47] + "..."
            desc_item = QTableWidgetItem(desc)
            self.table.setItem(row, 7, desc_item)
        
        # Resize columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 8):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
    
    def update_stats(self, status_data):
        """Update statistics display"""
        # Clear existing stats
        for i in reversed(range(self.stats_layout.count())):
            self.stats_layout.itemAt(i).widget().setParent(None)
        
        if not status_data:
            return
        
        history_info = status_data.get('history_info', {})
        cleanup_preview = status_data.get('cleanup_preview', {})
        settings = status_data.get('settings', {})
        
        # Create stat cards
        stats = [
            ("Total Datasets", history_info.get('total_datasets', 0), "#3498db"),
            ("Processed", history_info.get('processed_datasets', 0), "#27ae60"),
            ("Max Allowed", settings.get('max_datasets_allowed', 5), "#f39c12"),
            ("Pending Cleanup", cleanup_preview.get('datasets_to_be_deleted', 0), "#e74c3c")
        ]
        
        for title, value, color in stats:
            card = StatCard(title, value, color)
            self.stats_layout.addWidget(card)
    
    def on_selection_changed(self):
        """Handle table selection change"""
        selected_rows = self.table.selectionModel().selectedRows()
        self.delete_btn.setEnabled(len(selected_rows) > 0)
    
    def delete_selected(self):
        """Delete selected dataset"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        dataset = self.datasets[row]
        
        reply = QMessageBox.question(
            self, 'Delete Dataset',
            f'Are you sure you want to delete "{dataset.get("name", "Unnamed")}"?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.dataset_service.delete_dataset(dataset['id'])
                QMessageBox.information(self, "Success", "Dataset deleted successfully")
                self.dataset_deleted.emit()
                self.refresh_data()
            except DatasetException as e:
                QMessageBox.critical(self, "Error", f"Failed to delete dataset: {str(e)}")
    
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
    
    @pyqtSlot(str)
    def on_error(self, error_msg):
        """Handle error"""
        self.loading_label.setText(f"Error: {error_msg}")
        QMessageBox.critical(self, "Error", f"Failed to load history: {error_msg}")
    
    def refresh_data(self):
        """Refresh history data"""
        self.load_history()