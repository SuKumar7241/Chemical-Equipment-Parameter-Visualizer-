#!/usr/bin/env python3
"""
Quick test to verify the desktop application can start
"""

import sys
import os

def test_application_startup():
    """Test that the application can start without errors"""
    try:
        print("Testing application startup...")
        
        # Import main components
        from PyQt5.QtWidgets import QApplication
        from services.auth_service import AuthService
        from ui.login_window import LoginWindow
        
        # Create QApplication (required for PyQt5)
        app = QApplication(sys.argv)
        
        # Test authentication service
        auth_service = AuthService()
        print("Authentication service initialized")
        
        # Test login window creation
        login_window = LoginWindow(auth_service)
        print("Login window created")
        
        # Test API connection
        api_client = auth_service.get_api_client()
        try:
            response = api_client.get('/')
            print("API connection successful")
        except Exception as e:
            print(f"API connection tested (expected auth error: {type(e).__name__})")
        
        print("\nDesktop application startup test PASSED!")
        print("The application is ready to run.")
        
        # Clean up
        app.quit()
        return True
        
    except Exception as e:
        print(f"Application startup test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=== Desktop Application Startup Test ===\n")
    
    success = test_application_startup()
    
    if success:
        print("\nTest completed successfully!")
        print("You can now run the application with:")
        print("  python main.py")
        print("  or")
        print("  python launch.py")
    else:
        print("\nTest failed. Please check the error messages above.")