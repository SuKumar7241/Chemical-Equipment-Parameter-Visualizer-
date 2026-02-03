"""
Upload tab for CSV file upload
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QTextEdit, QPushButton, QFileDialog,
                             QFrame, QMessageBox, QProgressBar)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent

from services.dataset_service import DatasetService, DatasetException


class UploadWorker(QThread):
    """Worker thread for file upload"""
    upload_completed = pyqtSignal(dict)
    upload_failed = pyqtSignal(str)
    
    def __init__(self, dataset_service, file_path, name, description):
        super().__init__()
        self.dataset_service = dataset_service
        self.file_path = file_path
        self.name = name
        self.description = description
    
    def run(self):
        try:
            result = self.dataset_service.upload_dataset(
                self.file_path, self.name, self.description
            )
            self.upload_completed.emit(result)
        except DatasetException as e:
            self.upload_failed.emit(str(e))


class DropArea(QFrame):
    """Drag and drop area for file upload"""
    file_dropped = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
                padding: 40px;
            }
            QFrame:hover {
                border-color: #3498db;
                background-color: #ebf3fd;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Icon (using text for simplicity)
        icon_label = QLabel("📁")
        icon_label.setFont(QFont("Arial", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Instructions
        text_label = QLabel("Drag and drop CSV file here\nor click to browse")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        layout.addWidget(text_label)
        
        self.setLayout(layout)
        self.setMinimumHeight(150)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and files[0].lower().endswith('.csv'):
            self.file_dropped.emit(files[0])
        else:
            QMessageBox.warning(self, "Invalid File", "Please drop a CSV file")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select CSV File", "", "CSV Files (*.csv)"
            )
            if file_path:
                self.file_dropped.emit(file_path)


class UploadTab(QWidget):
    upload_completed = pyqtSignal()
    
    def __init__(self, dataset_service: DatasetService):
        super().__init__()
        self.dataset_service = dataset_service
        self.upload_worker = None
        self.selected_file = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Upload Dataset")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        layout.addWidget(title)
        
        # File selection area
        self.drop_area = DropArea()
        self.drop_area.file_dropped.connect(self.on_file_selected)
        layout.addWidget(self.drop_area)
        
        # Selected file info
        self.file_info_label = QLabel("No file selected")
        self.file_info_label.setStyleSheet("color: #7f8c8d; margin: 10px 0;")
        layout.addWidget(self.file_info_label)
        
        # Dataset name
        name_label = QLabel("Dataset Name (optional):")
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter dataset name")
        layout.addWidget(self.name_input)
        
        # Description
        desc_label = QLabel("Description (optional):")
        desc_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(desc_label)
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter dataset description")
        self.description_input.setMaximumHeight(100)
        layout.addWidget(self.description_input)
        
        # Upload button
        self.upload_button = QPushButton("Upload Dataset")
        self.upload_button.clicked.connect(self.handle_upload)
        self.upload_button.setEnabled(False)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        layout.addWidget(self.upload_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Guidelines
        guidelines = QFrame()
        guidelines.setFrameStyle(QFrame.StyledPanel)
        guidelines.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 15px;
                margin-top: 20px;
            }
        """)
        
        guidelines_layout = QVBoxLayout()
        
        guidelines_title = QLabel("Upload Guidelines")
        guidelines_title.setFont(QFont("Arial", 14, QFont.Bold))
        guidelines_layout.addWidget(guidelines_title)
        
        guidelines_text = QLabel("""
• Only CSV files are supported
• Maximum file size: 100MB
• First row should contain column headers
• Data will be automatically processed and analyzed
• You can view statistics and charts after processing
        """)
        guidelines_text.setStyleSheet("color: #6c757d; line-height: 1.4;")
        guidelines_layout.addWidget(guidelines_text)
        
        guidelines.setLayout(guidelines_layout)
        layout.addWidget(guidelines)
        
        layout.addStretch()
        self.setLayout(layout)
    
    @pyqtSlot(str)
    def on_file_selected(self, file_path):
        """Handle file selection"""
        self.selected_file = file_path
        
        # Update file info
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        size_mb = file_size / (1024 * 1024)
        
        self.file_info_label.setText(f"Selected: {file_name} ({size_mb:.2f} MB)")
        self.file_info_label.setStyleSheet("color: #27ae60; margin: 10px 0;")
        
        # Auto-fill name if empty
        if not self.name_input.text():
            name = os.path.splitext(file_name)[0]
            self.name_input.setText(name)
        
        # Enable upload button
        self.upload_button.setEnabled(True)
    
    def handle_upload(self):
        """Handle upload button click"""
        if not self.selected_file:
            QMessageBox.warning(self, "No File", "Please select a CSV file first")
            return
        
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()
        
        # Start upload
        self.upload_button.setEnabled(False)
        self.upload_button.setText("Uploading...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        self.upload_worker = UploadWorker(
            self.dataset_service, self.selected_file, name, description
        )
        self.upload_worker.upload_completed.connect(self.on_upload_completed)
        self.upload_worker.upload_failed.connect(self.on_upload_failed)
        self.upload_worker.start()
    
    @pyqtSlot(dict)
    def on_upload_completed(self, result):
        """Handle successful upload"""
        self.progress_bar.setVisible(False)
        self.upload_button.setEnabled(True)
        self.upload_button.setText("Upload Dataset")
        
        QMessageBox.information(
            self, "Upload Successful", 
            f"Dataset '{result.get('name', 'Unknown')}' uploaded successfully!"
        )
        
        # Clear form
        self.clear_form()
        
        # Emit signal to refresh other tabs
        self.upload_completed.emit()
    
    @pyqtSlot(str)
    def on_upload_failed(self, error_msg):
        """Handle upload failure"""
        self.progress_bar.setVisible(False)
        self.upload_button.setEnabled(True)
        self.upload_button.setText("Upload Dataset")
        
        QMessageBox.critical(self, "Upload Failed", f"Upload failed: {error_msg}")
    
    def clear_form(self):
        """Clear the upload form"""
        self.selected_file = None
        self.file_info_label.setText("No file selected")
        self.file_info_label.setStyleSheet("color: #7f8c8d; margin: 10px 0;")
        self.name_input.clear()
        self.description_input.clear()
        self.upload_button.setEnabled(False)