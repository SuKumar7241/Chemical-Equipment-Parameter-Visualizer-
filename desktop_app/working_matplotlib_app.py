#!/usr/bin/env python3
"""
Working Matplotlib Desktop App - Alternative approach
"""

import sys
import os
import matplotlib
# Use Agg backend first, then switch if needed
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont


class MatplotlibImageWidget(QWidget):
    """Widget that displays matplotlib plots as images"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('Matplotlib Desktop App - Working Version')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        demo_btn = QPushButton('Generate Demo Charts')
        demo_btn.clicked.connect(self.create_demo_charts)
        demo_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        button_layout.addWidget(demo_btn)
        
        analysis_btn = QPushButton('Show Data Analysis')
        analysis_btn.clicked.connect(self.create_analysis_charts)
        analysis_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(analysis_btn)
        
        layout.addLayout(button_layout)
        
        # Scroll area for images
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        
        layout.addWidget(self.scroll_area)
        
        # Status
        self.status_label = QLabel('Ready - Click buttons to generate matplotlib charts')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet('color: #666; padding: 10px;')
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def clear_charts(self):
        """Clear existing charts"""
        for i in reversed(range(self.scroll_layout.count())):
            child = self.scroll_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
    
    def add_chart_image(self, title, image_data):
        """Add a chart image to the display"""
        try:
            # Create frame for chart
            chart_frame = QFrame()
            chart_frame.setFrameStyle(QFrame.Box)
            chart_frame.setStyleSheet("border: 1px solid #ddd; margin: 5px;")
            
            frame_layout = QVBoxLayout()
            
            # Title
            title_label = QLabel(title)
            title_label.setFont(QFont('Arial', 12, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            frame_layout.addWidget(title_label)
            
            # Image
            image_label = QLabel()
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            image_label.setPixmap(pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_data = buffer.getvalue()
            buffer.close()
            
            plt.close()  # Close the figure to free memory
            
            return image_data
            
        except Exception as e:
            print(f"Error creating plot: {e}")
            return None
    
    def create_demo_charts(self):
        """Create demo charts"""
        self.clear_charts()
        self.status_label.setText('Generating demo charts...')
        
        try:
            # Chart 1: Pie Chart
            def pie_chart():
                labels = ['Python', 'JavaScript', 'Java', 'C++', 'Other']
                sizes = [35, 25, 20, 15, 5]
                colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
                plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            
            image_data = self.create_matplotlib_plot(pie_chart, 'Programming Languages Distribution')
            if image_data:
                self.add_chart_image('Pie Chart - Programming Languages', image_data)
            
            # Chart 2: Bar Chart
            def bar_chart():
                categories = ['Q1', 'Q2', 'Q3', 'Q4']
                values = [23, 45, 56, 78]
                bars = plt.bar(categories, values, color='lightblue')
                plt.ylabel('Sales (K)')
                for bar, value in zip(bars, values):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                            str(value), ha='center', va='bottom')
            
            image_data = self.create_matplotlib_plot(bar_chart, 'Quarterly Sales')
            if image_data:
                self.add_chart_image('Bar Chart - Quarterly Sales', image_data)
            
            # Chart 3: Line Chart
            def line_chart():
                x = np.linspace(0, 10, 100)
                y1 = np.sin(x)
                y2 = np.cos(x)
                plt.plot(x, y1, 'b-', label='sin(x)', linewidth=2)
                plt.plot(x, y2, 'r--', label='cos(x)', linewidth=2)
                plt.xlabel('X')
                plt.ylabel('Y')
                plt.legend()
                plt.grid(True, alpha=0.3)
            
            image_data = self.create_matplotlib_plot(line_chart, 'Trigonometric Functions')
            if image_data:
                self.add_chart_image('Line Chart - Trigonometric Functions', image_data)
            
            # Chart 4: Scatter Plot
            def scatter_chart():
                np.random.seed(42)
                x = np.random.randn(100)
                y = 2 * x + np.random.randn(100)
                plt.scatter(x, y, alpha=0.6, color='green')
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                plt.plot(x, p(x), "r--", alpha=0.8)
                plt.xlabel('X values')
                plt.ylabel('Y values')
            
            image_data = self.create_matplotlib_plot(scatter_chart, 'Scatter Plot with Trend Line')
            if image_data:
                self.add_chart_image('Scatter Plot - Data Correlation', image_data)
            
            self.status_label.setText('Demo charts generated successfully!')
            
        except Exception as e:
            self.status_label.setText(f'Error generating charts: {str(e)}')
            print(f"Demo charts error: {e}")
    
    def create_analysis_charts(self):
        """Create data analysis charts"""
        self.clear_charts()
        self.status_label.setText('Generating data analysis charts...')
        
        try:
            # Analysis Chart 1: Data Types
            def data_types_chart():
                data_types = ['int64', 'float64', 'object']
                counts = [3, 2, 2]
                colors = ['#ff9999', '#66b3ff', '#99ff99']
                plt.pie(counts, labels=data_types, autopct='%1.1f%%', colors=colors, startangle=90)
            
            image_data = self.create_matplotlib_plot(data_types_chart, 'Data Types Distribution')
            if image_data:
                self.add_chart_image('Dataset Analysis - Data Types', image_data)
            
            # Analysis Chart 2: Missing Values
            def missing_values_chart():
                columns = ['age', 'salary', 'department', 'rating']
                missing_counts = [1, 1, 1, 1]
                bars = plt.bar(range(len(missing_counts)), missing_counts, color='lightcoral')
                plt.xlabel('Columns')
                plt.ylabel('Missing Values Count')
                plt.xticks(range(len(columns)), columns, rotation=45)
                for bar, value in zip(bars, missing_counts):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                            str(value), ha='center', va='bottom')
            
            image_data = self.create_matplotlib_plot(missing_values_chart, 'Missing Values Analysis')
            if image_data:
                self.add_chart_image('Dataset Analysis - Missing Values', image_data)
            
            # Analysis Chart 3: Numeric Statistics
            def numeric_stats_chart():
                columns = ['id', 'age', 'salary', 'rating']
                means = [5.5, 33.2, 75400, 4.4]
                bars = plt.bar(range(len(means)), means, color='lightblue')
                plt.xlabel('Numeric Columns')
                plt.ylabel('Mean Values')
                plt.xticks(range(len(columns)), columns, rotation=45)
                for bar, value in zip(bars, means):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(means)*0.01,
                            f'{value:.1f}', ha='center', va='bottom')
            
            image_data = self.create_matplotlib_plot(numeric_stats_chart, 'Numeric Columns Statistics')
            if image_data:
                self.add_chart_image('Dataset Analysis - Numeric Statistics', image_data)
            
            self.status_label.setText('Data analysis charts generated successfully!')
            
        except Exception as e:
            self.status_label.setText(f'Error generating analysis: {str(e)}')
            print(f"Analysis charts error: {e}")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Chemical Equipment Parameter Visualizer - Matplotlib Version')
        self.setGeometry(100, 100, 900, 700)
        
        # Create central widget
        central_widget = MatplotlibImageWidget()
        self.setCentralWidget(central_widget)
        
        # Status bar
        self.statusBar().showMessage('Matplotlib Desktop App Ready - Using Agg backend with image display')


def main():
    """Main function"""
    try:
        print("Starting Matplotlib Desktop App...")
        print(f"Matplotlib version: {matplotlib.__version__}")
        print(f"Matplotlib backend: {matplotlib.get_backend()}")
        
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName('Matplotlib Desktop App')
        
        # Create and show main window
        main_window = MainWindow()
        main_window.show()
        
        print("Application started successfully!")
        print("Click the buttons to generate matplotlib charts.")
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            QMessageBox.critical(None, 'Error', f'Failed to start application:\n{str(e)}')
        except:
            pass
        
        sys.exit(1)


if __name__ == '__main__':
    main()