#!/usr/bin/env python3
"""
Standalone Matplotlib Demo - No Backend Required
Shows matplotlib integration working in desktop app
"""

import sys
import os
from datetime import datetime

# Set matplotlib backend BEFORE any other matplotlib imports
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import matplotlib components
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class MatplotlibDemoWidget(QWidget):
    """Standalone matplotlib demo widget"""
    
    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(12, 8), facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.init_ui()
        self.create_demo_charts()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('Matplotlib Integration Demo')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info
        info = QLabel('This demonstrates matplotlib charts embedded in PyQt5 desktop application')
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet('color: #666; margin-bottom: 10px;')
        layout.addWidget(info)
        
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
        
        sample_btn = QPushButton('Show Sample Data Analysis')
        sample_btn.clicked.connect(self.create_sample_analysis)
        sample_btn.setStyleSheet("""
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
        button_layout.addWidget(sample_btn)
        
        clear_btn = QPushButton('Clear Charts')
        clear_btn.clicked.connect(self.clear_charts)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # Chart area
        chart_frame = QFrame()
        chart_frame.setFrameStyle(QFrame.Box)
        chart_frame.setStyleSheet("border: 2px solid #ddd; border-radius: 5px;")
        chart_layout = QVBoxLayout()
        chart_layout.addWidget(self.canvas)
        chart_frame.setLayout(chart_layout)
        layout.addWidget(chart_frame)
        
        # Status
        self.status_label = QLabel('Ready - Click buttons to see matplotlib charts')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet('color: #666; padding: 10px;')
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def create_demo_charts(self):
        """Create demo charts showing matplotlib capabilities"""
        try:
            self.figure.clear()
            
            # Create 2x2 subplot grid
            gs = self.figure.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
            # 1. Pie Chart
            ax1 = self.figure.add_subplot(gs[0, 0])
            labels = ['Python', 'JavaScript', 'Java', 'C++', 'Other']
            sizes = [35, 25, 20, 15, 5]
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax1.set_title('Programming Languages', fontweight='bold')
            
            # 2. Bar Chart
            ax2 = self.figure.add_subplot(gs[0, 1])
            categories = ['Q1', 'Q2', 'Q3', 'Q4']
            values = [23, 45, 56, 78]
            bars = ax2.bar(categories, values, color='lightblue')
            ax2.set_title('Quarterly Sales', fontweight='bold')
            ax2.set_ylabel('Sales (K)')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        str(value), ha='center', va='bottom')
            
            # 3. Line Chart
            ax3 = self.figure.add_subplot(gs[1, 0])
            x = np.linspace(0, 10, 100)
            y1 = np.sin(x)
            y2 = np.cos(x)
            ax3.plot(x, y1, 'b-', label='sin(x)', linewidth=2)
            ax3.plot(x, y2, 'r--', label='cos(x)', linewidth=2)
            ax3.set_title('Trigonometric Functions', fontweight='bold')
            ax3.set_xlabel('X')
            ax3.set_ylabel('Y')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # 4. Scatter Plot
            ax4 = self.figure.add_subplot(gs[1, 1])
            np.random.seed(42)
            x = np.random.randn(100)
            y = 2 * x + np.random.randn(100)
            ax4.scatter(x, y, alpha=0.6, color='green')
            ax4.set_title('Scatter Plot', fontweight='bold')
            ax4.set_xlabel('X values')
            ax4.set_ylabel('Y values')
            
            # Add trend line
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            ax4.plot(x, p(x), "r--", alpha=0.8)
            
            self.canvas.draw()
            self.status_label.setText('✅ Demo charts created successfully!')
            
        except Exception as e:
            self.status_label.setText(f'❌ Error creating charts: {str(e)}')
            print(f"Chart error: {e}")
    
    def create_sample_analysis(self):
        """Create sample data analysis charts (like the real app would show)"""
        try:
            self.figure.clear()
            
            # Simulate dataset analysis
            gs = self.figure.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
            # 1. Data Types Distribution (Pie Chart)
            ax1 = self.figure.add_subplot(gs[0, 0])
            data_types = ['int64', 'float64', 'object']
            type_counts = [3, 2, 2]  # Simulated counts
            colors = plt.cm.Set3(np.linspace(0, 1, len(data_types)))
            ax1.pie(type_counts, labels=data_types, autopct='%1.1f%%', colors=colors, startangle=90)
            ax1.set_title('Data Types Distribution', fontsize=12, fontweight='bold')
            
            # 2. Missing Values Analysis (Bar Chart)
            ax2 = self.figure.add_subplot(gs[0, 1])
            columns = ['age', 'salary', 'dept', 'rating']
            missing_counts = [1, 1, 1, 1]  # Simulated missing values
            bars = ax2.bar(range(len(missing_counts)), missing_counts, color='lightcoral')
            ax2.set_xlabel('Columns')
            ax2.set_ylabel('Missing Values Count')
            ax2.set_title('Missing Values by Column', fontsize=12, fontweight='bold')
            ax2.set_xticks(range(len(columns)))
            ax2.set_xticklabels(columns, rotation=45, ha='right')
            
            # Add value labels
            for bar, value in zip(bars, missing_counts):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                        str(value), ha='center', va='bottom', fontsize=8)
            
            # 3. Numeric Statistics (Bar Chart)
            ax3 = self.figure.add_subplot(gs[1, 0])
            numeric_cols = ['id', 'age', 'salary', 'rating']
            means = [5.5, 33.2, 75400, 4.4]  # Simulated means
            bars = ax3.bar(range(len(means)), means, color='lightblue')
            ax3.set_xlabel('Numeric Columns')
            ax3.set_ylabel('Mean Values')
            ax3.set_title('Mean Values of Numeric Columns', fontsize=12, fontweight='bold')
            ax3.set_xticks(range(len(numeric_cols)))
            ax3.set_xticklabels(numeric_cols, rotation=45, ha='right')
            
            # Add value labels
            for bar, value in zip(bars, means):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(means)*0.01,
                        f'{value:.1f}', ha='center', va='bottom', fontsize=8)
            
            # 4. Dataset Summary (Text)
            ax4 = self.figure.add_subplot(gs[1, 1])
            ax4.axis('off')
            
            summary_text = f"""Dataset Summary

Total Columns: 7
Numeric Columns: 4
Text Columns: 3
Total Missing Values: 4

Analysis completed at:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This demonstrates the same
chart types that would appear
in the full application when
analyzing real CSV data."""
            
            ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=10,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
            
            self.canvas.draw()
            self.status_label.setText('✅ Sample data analysis charts created!')
            
        except Exception as e:
            self.status_label.setText(f'❌ Error creating analysis: {str(e)}')
            print(f"Analysis error: {e}")
    
    def clear_charts(self):
        """Clear all charts"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Charts cleared\nClick buttons above to generate new charts', 
               ha='center', va='center', fontsize=16, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.canvas.draw()
        self.status_label.setText('Charts cleared - Ready for new charts')


class MainWindow(QMainWindow):
    """Main demo window"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Matplotlib Desktop App Demo - Screening Task')
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        central_widget = MatplotlibDemoWidget()
        self.setCentralWidget(central_widget)
        
        # Status bar
        self.statusBar().showMessage(f'Matplotlib backend: {matplotlib.get_backend()} | Ready for demonstration')


def main():
    """Main function"""
    try:
        print("🎯 MATPLOTLIB DESKTOP APP DEMO")
        print("=" * 50)
        print("Starting standalone matplotlib demonstration...")
        print(f"Matplotlib backend: {matplotlib.get_backend()}")
        
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName('Matplotlib Demo')
        
        # Apply styling
        app.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                font-family: Arial, sans-serif;
            }
        """)
        
        # Create and show main window
        main_window = MainWindow()
        main_window.show()
        
        print("✅ Demo window opened successfully!")
        print("\nDemo Instructions:")
        print("1. Click 'Generate Demo Charts' to see various matplotlib chart types")
        print("2. Click 'Show Sample Data Analysis' to see dataset analysis charts")
        print("3. Click 'Clear Charts' to clear the display")
        print("\nThis demonstrates matplotlib integration for your screening task!")
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error dialog
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            QMessageBox.critical(None, 'Demo Error', f'Failed to start demo:\n{str(e)}')
        except:
            pass
        
        sys.exit(1)


if __name__ == '__main__':
    main()