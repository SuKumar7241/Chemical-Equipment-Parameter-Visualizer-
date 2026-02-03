#!/usr/bin/env python3
"""
Debug script to test imports step by step
"""

def test_imports():
    """Test each import individually to find the problem"""
    
    print("=== Testing Imports Step by Step ===\n")
    
    # Test 1: Basic PyQt5
    try:
        print("1. Testing PyQt5 basic imports...")
        from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QIcon
        print("   ✓ PyQt5 basic imports - OK")
    except Exception as e:
        print(f"   ❌ PyQt5 basic imports - FAILED: {e}")
        return False
    
    # Test 2: Services
    try:
        print("2. Testing services imports...")
        from services.auth_service import AuthService
        print("   ✓ AuthService import - OK")
    except Exception as e:
        print(f"   ❌ AuthService import - FAILED: {e}")
        print("   Error details:", str(e))
        return False
    
    # Test 3: API Client
    try:
        print("3. Testing API client...")
        from services.api_client import APIClient
        print("   ✓ APIClient import - OK")
    except Exception as e:
        print(f"   ❌ APIClient import - FAILED: {e}")
        return False
    
    # Test 4: Login Window
    try:
        print("4. Testing login window import...")
        from ui.login_window import LoginWindow
        print("   ✓ LoginWindow import - OK")
    except Exception as e:
        print(f"   ❌ LoginWindow import - FAILED: {e}")
        print("   Error details:", str(e))
        return False
    
    # Test 5: Main Window
    try:
        print("5. Testing main window import...")
        from ui.main_window import MainWindow
        print("   ✓ MainWindow import - OK")
    except Exception as e:
        print(f"   ❌ MainWindow import - FAILED: {e}")
        print("   Error details:", str(e))
        return False
    
    # Test 6: Create AuthService instance
    try:
        print("6. Testing AuthService instantiation...")
        auth_service = AuthService()
        print("   ✓ AuthService instance - OK")
    except Exception as e:
        print(f"   ❌ AuthService instance - FAILED: {e}")
        print("   Error details:", str(e))
        return False
    
    # Test 7: Create LoginWindow instance
    try:
        print("7. Testing LoginWindow instantiation...")
        app = QApplication([])  # Need QApplication for widgets
        login_window = LoginWindow(auth_service)
        print("   ✓ LoginWindow instance - OK")
        app.quit()
    except Exception as e:
        print(f"   ❌ LoginWindow instance - FAILED: {e}")
        print("   Error details:", str(e))
        return False
    
    print("\n🎉 All imports and instantiations successful!")
    print("The issue might be in the main application logic.")
    return True

if __name__ == '__main__':
    success = test_imports()
    
    if success:
        print("\n✅ All components are working individually.")
        print("Let's try a simplified main application...")
    else:
        print("\n❌ Found the problem! Check the error details above.")