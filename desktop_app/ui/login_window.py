"""
Login window for authentication
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QTabWidget,
                             QFormLayout, QFrame)
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont
from services.auth_service import AuthService


class AuthWorker(QThread):
    """Worker thread for authentication to prevent UI blocking"""
    finished = pyqtSignal(dict)
    
    def __init__(self, auth_service, action, **kwargs):
        super().__init__()
        self.auth_service = auth_service
        self.action = action
        self.kwargs = kwargs
    
    def run(self):
        if self.action == 'login':
            result = self.auth_service.login(
                self.kwargs['username'], 
                self.kwargs['password']
            )
        elif self.action == 'register':
            result = self.auth_service.register(
                self.kwargs['username'],
                self.kwargs['password'],
                self.kwargs['email']
            )
        else:
            result = {'success': False, 'error': 'Unknown action'}
        
        self.finished.emit(result)


class LoginWindow(QWidget):
    login_successful = pyqtSignal()
    
    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.auth_worker = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Chemical Equipment Parameter Visualizer")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 20px 0;")
        layout.addWidget(title)
        
        # Create tab widget for login/register
        self.tab_widget = QTabWidget()
        
        # Login tab
        login_tab = self.create_login_tab()
        self.tab_widget.addTab(login_tab, "Login")
        
        # Register tab
        register_tab = self.create_register_tab()
        self.tab_widget.addTab(register_tab, "Register")
        
        layout.addWidget(self.tab_widget)
        
        # Center the form
        layout.addStretch()
        
        self.setLayout(layout)
        self.setFixedSize(400, 350)
        self.setWindowTitle("Login - Chemical Equipment Parameter Visualizer")
    
    def create_login_tab(self):
        """Create login form"""
        widget = QWidget()
        layout = QFormLayout()
        
        # Username field
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Enter username")
        layout.addRow("Username:", self.login_username)
        
        # Password field
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setPlaceholderText("Enter password")
        layout.addRow("Password:", self.login_password)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        layout.addRow("", self.login_button)
        
        # Connect Enter key to login
        self.login_password.returnPressed.connect(self.handle_login)
        
        widget.setLayout(layout)
        return widget
    
    def create_register_tab(self):
        """Create registration form"""
        widget = QWidget()
        layout = QFormLayout()
        
        # Username field
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Choose username")
        layout.addRow("Username:", self.register_username)
        
        # Email field
        self.register_email = QLineEdit()
        self.register_email.setPlaceholderText("Enter email address")
        layout.addRow("Email:", self.register_email)
        
        # Password field
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_password.setPlaceholderText("Choose password")
        layout.addRow("Password:", self.register_password)
        
        # Confirm password field
        self.register_confirm = QLineEdit()
        self.register_confirm.setEchoMode(QLineEdit.Password)
        self.register_confirm.setPlaceholderText("Confirm password")
        layout.addRow("Confirm:", self.register_confirm)
        
        # Register button
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.handle_register)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        layout.addRow("", self.register_button)
        
        widget.setLayout(layout)
        return widget
    
    def handle_login(self):
        """Handle login button click"""
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
        
        self.login_button.setEnabled(False)
        self.login_button.setText("Logging in...")
        
        # Start authentication in worker thread
        self.auth_worker = AuthWorker(self.auth_service, 'login', 
                                     username=username, password=password)
        self.auth_worker.finished.connect(self.on_auth_finished)
        self.auth_worker.start()
    
    def handle_register(self):
        """Handle register button click"""
        username = self.register_username.text().strip()
        email = self.register_email.text().strip()
        password = self.register_password.text()
        confirm = self.register_confirm.text()
        
        if not all([username, email, password, confirm]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        self.register_button.setEnabled(False)
        self.register_button.setText("Registering...")
        
        # Start registration in worker thread
        self.auth_worker = AuthWorker(self.auth_service, 'register',
                                     username=username, password=password, email=email)
        self.auth_worker.finished.connect(self.on_auth_finished)
        self.auth_worker.start()
    
    @pyqtSlot(dict)
    def on_auth_finished(self, result):
        """Handle authentication result"""
        # Re-enable buttons
        self.login_button.setEnabled(True)
        self.login_button.setText("Login")
        self.register_button.setEnabled(True)
        self.register_button.setText("Register")
        
        if result['success']:
            self.login_successful.emit()
        else:
            QMessageBox.critical(self, "Authentication Failed", result.get('error', 'Unknown error'))
    
    def clear_form(self):
        """Clear all form fields"""
        self.login_username.clear()
        self.login_password.clear()
        self.register_username.clear()
        self.register_email.clear()
        self.register_password.clear()
        self.register_confirm.clear()
        self.tab_widget.setCurrentIndex(0)  # Switch to login tab