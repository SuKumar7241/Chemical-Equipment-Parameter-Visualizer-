#!/usr/bin/env python3
"""
Simplified version of the desktop app - minimal working version
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QLineEdit, QPushButton, QMessageBox,
                             QTabWidget, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SimpleLoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Dataset Analyzer - Simple Login")
        self.setGeometry(300, 300, 400, 300)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Dataset Analyzer")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
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
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.handle_register)
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        button_layout.addWidget(login_btn)
        button_layout.addWidget(register_btn)
        layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("Ready to login")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; margin: 10px;")
        layout.addWidget(self.status_label)
        
        # Instructions
        instructions = QLabel("""
Instructions:
1. This is a simplified version of the desktop app
2. Enter any username and password to test
3. Click Login or Register to see the functionality
4. The full app will connect to the Django backend
        """)
        instructions.setStyleSheet("color: #666; font-size: 11px; margin: 10px;")
        layout.addWidget(instructions)
        
        self.setLayout(layout)
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
        
        self.status_label.setText(f"Login attempt for: {username}")
        QMessageBox.information(self, "Login Test", 
                               f"Login functionality works!\nUsername: {username}\n\n"
                               "In the full app, this would connect to the Django backend.")
    
    def handle_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
        
        self.status_label.setText(f"Registration for: {username}")
        QMessageBox.information(self, "Register Test", 
                               f"Registration functionality works!\nUsername: {username}\n\n"
                               "In the full app, this would create an account via Django backend.")

def main():
    print("=== Simple Dataset Analyzer Desktop App ===")
    print("Starting simplified version...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Dataset Analyzer - Simple")
    
    window = SimpleLoginWindow()
    window.show()
    window.raise_()
    window.activateWindow()
    
    print("Simple login window should be visible!")
    print("This tests the basic PyQt5 functionality without complex imports.")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()