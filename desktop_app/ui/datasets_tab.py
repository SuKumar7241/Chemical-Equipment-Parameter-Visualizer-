"""
Datasets tab for viewing and managing datasets
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                             QHeaderView, QAbstractItemView, QFrame, QSplitter,
                             QTextEdit, QTabWidget)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from services.dataset_service import DatasetService, DatasetException


class DatasetsWorker(QThread):
    """Worker thread for loading datasets"""
    data_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, dataset_service):
        super().__init__()
        self.dataset_service = dataset_service
    
    def run(self):
        try:
            datasets = self.dataset_service.get_datasets()
            self.data_loaded.emit(datasets)
        except DatasetException as e:
            self.error_occurred.emit(str(e))


class DatasetDetailWorker(QThread):
    """Worker thread for loading dataset details"""
    details_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, dataset_service, dataset_id):
        super().__init__()
        self.dataset_service = dataset_service
        self.dataset_id = dataset_id
    
    def run(self):
        try:
            dataset = self.dataset_service.get_dataset(self.dataset_id)
            
            details = {'dataset': dataset}
            
            # Get statistics if processed
            if dataset.get('is_processed'):
                try:
                    stats = self.dataset_service.get_dataset_statistics(self.dataset_id)
                    details['statistics'] = stats
                except DatasetException:
                    pass
                
                try:
                    columns = self.dataset_service.get_dataset_columns(self.dataset_id)
                    details['columns'] = columns
                except DatasetException:
                    pass
            
            self.details_loaded.emit(details)
            
        except DatasetException as e:
            self.error_occurred.emit(str(e))


class ChartWidget(QWidget):
    """Widget for displaying matplotlib charts"""
    
    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def clear_chart(self):
        """Clear the chart"""
        self.figure.clear()
        self.canvas.draw()
    
    def plot_statistics(self, statistics, columns):
        """Plot dataset statistics"""
        self.figure.clear()
        
        if not statistics or not statistics.get('statistics_data'):
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No statistics available', 
                   ha='center', va='center', transform=ax.transAxes)
            self.canvas.draw()
            return
        
        stats_data = statistics['statistics_data']
        
        # Create subplots
        if len(columns) > 0:
            fig_rows = 2
            fig_cols = 2
        else:
            fig_rows = 1
            fig_cols = 1
        
        # Plot 1: Numeric column means (if available)
        numeric_cols = []
        numeric_means = []
        
        for col_name, col_stats in stats_data.items():
            if isinstance(col_stats, dict) and 'mean' in col_stats:
                numeric_cols.append(col_name)
                numeric_means.append(col_stats['mean'])
        
        if numeric_cols:
            ax1 = self.figure.add_subplot(fig_rows, fig_cols, 1)
            bars = ax1.bar(range(len(numeric_cols)), numeric_means, color='skyblue')
            ax1.set_title('Numeric Column Means')
            ax1.set_xlabel('Columns')
            ax1.set_ylabel('Mean Value')
            ax1.set_xticks(range(len(numeric_cols)))
            ax1.set_xticklabels(numeric_cols, rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, value in zip(bars, numeric_means):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value:.2f}', ha='center', va='bottom')
        
        # Plot 2: Data type distribution
        if columns:
            data_types = {}
            for col in columns:
                dtype = col.get('data_type', 'unknown')
                data_types[dtype] = data_types.get(dtype, 0) + 1
            
            if data_types:
                ax2 = self.figure.add_subplot(fig_rows, fig_cols, 2)
                colors = plt.cm.Set3(np.linspace(0, 1, len(data_types)))
                wedges, texts, autotexts = ax2.pie(
                    data_types.values(), 
                    labels=data_types.keys(),
                    autopct='%1.1f%%',
                    colors=colors
                )
                ax2.set_title('Data Type Distribution')
        
        # Plot 3: Missing values (if available)
        if columns:
            col_names = [col['column_name'] for col in columns[:10]]  # Limit to 10 columns
            null_counts = [col.get('null_count', 0) for col in columns[:10]]
            
            if any(null_counts):
                ax3 = self.figure.add_subplot(fig_rows, fig_cols, 3)
                bars = ax3.bar(range(len(col_names)), null_counts, color='lightcoral')
                ax3.set_title('Missing Values by Column (Top 10)')
                ax3.set_xlabel('Columns')
                ax3.set_ylabel('Null Count')
                ax3.set_xticks(range(len(col_names)))
                ax3.set_xticklabels(col_names, rotation=45, ha='right')
        
        # Plot 4: Basic statistics summary
        if statistics:
            ax4 = self.figure.add_subplot(fig_rows, fig_cols, 4)
            
            stats_summary = [
                ('Total Records', statistics.get('total_records', 0)),
                ('Numeric Columns', statistics.get('numeric_columns_count', 0)),
                ('Categorical Columns', statistics.get('categorical_columns_count', 0)),
                ('Missing Values', statistics.get('missing_values_count', 0))
            ]
            
            labels, values = zip(*stats_summary)
            bars = ax4.bar(range(len(labels)), values, color='lightgreen')
            ax4.set_title('Dataset Summary')
            ax4.set_xticks(range(len(labels)))
            ax4.set_xticklabels(labels, rotation=45, ha='right')
            
            # Add value labels
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value}', ha='center', va='bottom')
        
        self.figure.tight_layout()
        self.canvas.draw()


class DatasetsTab(QWidget):
    dataset_deleted = pyqtSignal()
    
    def __init__(self, dataset_service: DatasetService):
        super().__init__()
        self.dataset_service = dataset_service
        self.datasets_worker = None
        self.detail_worker = None
        self.datasets = []
        self.init_ui()
        self.load_datasets()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title and refresh button
        header_layout = QHBoxLayout()
        
        title = QLabel("Datasets")
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
        
        # Create splitter for table and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Datasets table
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        left_layout.addWidget(self.table)
        
        # Delete and PDF buttons
        buttons_layout = QHBoxLayout()
        
        self.pdf_btn = QPushButton("📄 Download PDF Report")
        self.pdf_btn.clicked.connect(self.download_pdf_report)
        self.pdf_btn.setEnabled(False)
        self.pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        buttons_layout.addWidget(self.pdf_btn)
        
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
        buttons_layout.addWidget(self.delete_btn)
        
        left_layout.addLayout(buttons_layout)
        
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)
        
        # Right side: Dataset details
        self.details_widget = QTabWidget()
        
        # Overview tab
        self.overview_tab = QWidget()
        overview_layout = QVBoxLayout()
        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        overview_layout.addWidget(self.overview_text)
        self.overview_tab.setLayout(overview_layout)
        self.details_widget.addTab(self.overview_tab, "Overview")
        
        # Charts tab
        self.charts_tab = QWidget()
        charts_layout = QVBoxLayout()
        self.chart_widget = ChartWidget()
        charts_layout.addWidget(self.chart_widget)
        self.charts_tab.setLayout(charts_layout)
        self.details_widget.addTab(self.charts_tab, "Charts")
        
        splitter.addWidget(self.details_widget)
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
        
        # Loading label
        self.loading_label = QLabel("Loading datasets...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(self.loading_label)
        
        self.setLayout(layout)
    
    def load_datasets(self):
        """Load datasets in background thread"""
        if self.datasets_worker and self.datasets_worker.isRunning():
            return
        
        self.loading_label.show()
        self.table.setRowCount(0)
        
        self.datasets_worker = DatasetsWorker(self.dataset_service)
        self.datasets_worker.data_loaded.connect(self.on_datasets_loaded)
        self.datasets_worker.error_occurred.connect(self.on_error)
        self.datasets_worker.start()
    
    @pyqtSlot(list)
    def on_datasets_loaded(self, datasets):
        """Handle loaded datasets"""
        self.loading_label.hide()
        self.datasets = datasets
        
        # Setup table
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Name", "File Name", "Rows", "Columns", "Upload Date", "Status", "Size"
        ])
        
        self.table.setRowCount(len(datasets))
        
        for row, dataset in enumerate(datasets):
            # Name
            name_item = QTableWidgetItem(dataset.get('name', 'Unnamed'))
            self.table.setItem(row, 0, name_item)
            
            # File name
            file_item = QTableWidgetItem(dataset.get('file_name', ''))
            self.table.setItem(row, 1, file_item)
            
            # Rows
            rows_item = QTableWidgetItem(f"{dataset.get('total_rows', 0):,}")
            self.table.setItem(row, 2, rows_item)
            
            # Columns
            cols_item = QTableWidgetItem(str(dataset.get('total_columns', 0)))
            self.table.setItem(row, 3, cols_item)
            
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
            self.table.setItem(row, 4, date_item)
            
            # Status
            status = "Processed" if dataset.get('is_processed') else "Processing"
            status_item = QTableWidgetItem(status)
            self.table.setItem(row, 5, status_item)
            
            # Size
            file_size = dataset.get('file_size', 0)
            if file_size:
                size_mb = file_size / (1024 * 1024)
                size_str = f"{size_mb:.2f} MB"
            else:
                size_str = "N/A"
            size_item = QTableWidgetItem(size_str)
            self.table.setItem(row, 6, size_item)
        
        # Resize columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
    
    def on_selection_changed(self):
        """Handle table selection change"""
        selected_rows = self.table.selectionModel().selectedRows()
        
        if selected_rows:
            row = selected_rows[0].row()
            dataset = self.datasets[row]
            is_processed = dataset.get('is_processed', False)
            
            self.delete_btn.setEnabled(True)
            self.pdf_btn.setEnabled(is_processed)  # Only enable PDF for processed datasets
            
            self.load_dataset_details(dataset['id'])
        else:
            self.delete_btn.setEnabled(False)
            self.pdf_btn.setEnabled(False)
            self.clear_details()
    
    def load_dataset_details(self, dataset_id):
        """Load dataset details"""
        if self.detail_worker and self.detail_worker.isRunning():
            self.detail_worker.terminate()
        
        self.overview_text.setText("Loading details...")
        self.chart_widget.clear_chart()
        
        self.detail_worker = DatasetDetailWorker(self.dataset_service, dataset_id)
        self.detail_worker.details_loaded.connect(self.on_details_loaded)
        self.detail_worker.error_occurred.connect(self.on_details_error)
        self.detail_worker.start()
    
    @pyqtSlot(dict)
    def on_details_loaded(self, details):
        """Handle loaded dataset details"""
        dataset = details['dataset']
        statistics = details.get('statistics')
        columns = details.get('columns', [])
        
        # Update overview
        overview_text = f"""
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
        
        if statistics:
            overview_text += f"""

Statistics:
- Total Records: {statistics.get('total_records', 0):,}
- Numeric Columns: {statistics.get('numeric_columns_count', 0)}
- Categorical Columns: {statistics.get('categorical_columns_count', 0)}
- Missing Values: {statistics.get('missing_values_count', 0)}
            """
            
            # Equipment-specific stats
            if statistics.get('avg_flowrate'):
                overview_text += f"\n- Avg Flow Rate: {statistics['avg_flowrate']:.2f}"
            if statistics.get('avg_pressure'):
                overview_text += f"\n- Avg Pressure: {statistics['avg_pressure']:.2f}"
            if statistics.get('avg_temperature'):
                overview_text += f"\n- Avg Temperature: {statistics['avg_temperature']:.2f}"
        
        self.overview_text.setText(overview_text)
        
        # Update charts
        if dataset.get('is_processed'):
            self.chart_widget.plot_statistics(statistics, columns)
    
    @pyqtSlot(str)
    def on_details_error(self, error_msg):
        """Handle details loading error"""
        self.overview_text.setText(f"Error loading details: {error_msg}")
    
    def clear_details(self):
        """Clear dataset details"""
        self.overview_text.setText("Select a dataset to view details")
        self.chart_widget.clear_chart()
    
    def download_pdf_report(self):
        """Download PDF report for selected dataset"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        dataset = self.datasets[row]
        dataset_id = dataset['id']
        dataset_name = dataset.get('name', 'dataset')
        
        try:
            # Get PDF data from API
            pdf_data = self.dataset_service.download_pdf_report(dataset_id)
            
            # Save PDF file
            from PyQt5.QtWidgets import QFileDialog
            import os
            
            # Suggest filename
            suggested_name = f"{dataset_name}_report.pdf"
            
            # Open file dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF Report",
                suggested_name,
                "PDF Files (*.pdf);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(pdf_data)
                
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"PDF report saved successfully to:\n{file_path}"
                )
                
                # Ask if user wants to open the file
                reply = QMessageBox.question(
                    self,
                    "Open PDF",
                    "Would you like to open the PDF report now?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    import subprocess
                    import platform
                    
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
                            f"PDF saved but couldn't open automatically: {str(e)}"
                        )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to download PDF report: {str(e)}"
            )

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
    
    @pyqtSlot(str)
    def on_error(self, error_msg):
        """Handle error"""
        self.loading_label.setText(f"Error: {error_msg}")
        QMessageBox.critical(self, "Error", f"Failed to load datasets: {error_msg}")
    
    def refresh_data(self):
        """Refresh datasets data"""
        self.clear_details()
        self.load_datasets()