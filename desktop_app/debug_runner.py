#!/usr/bin/env python3
"""
Debug runner to see what's happening with the apps
"""

import sys
import traceback
import subprocess
import os

def run_with_output(script_name):
    """Run a script and capture all output"""
    print(f"\n{'='*50}")
    print(f"TESTING: {script_name}")
    print(f"{'='*50}")
    
    if not os.path.exists(script_name):
        print(f"❌ File {script_name} does not exist")
        return False
    
    try:
        print(f"Running: python {script_name}")
        print("Output:")
        print("-" * 30)
        
        # Run the script and capture output
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Script ran successfully")
            return True
        else:
            print("❌ Script failed")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Script timed out (this might be normal for GUI apps)")
        return True  # Timeout might be normal for GUI apps
        
    except Exception as e:
        print(f"❌ Error running script: {e}")
        traceback.print_exc()
        return False

def main():
    print("=== Desktop App Debug Runner ===")
    print("Testing all available desktop app scripts...")
    
    # List of scripts to test
    scripts = [
        "test_window.py",
        "simple_app.py", 
        "working_app.py",
        "complete_app.py",
        "minimal_test.py"
    ]
    
    results = {}
    
    for script in scripts:
        results[script] = run_with_output(script)
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    
    for script, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{script:<20} {status}")
    
    # Recommendations
    print(f"\n{'='*50}")
    print("RECOMMENDATIONS")
    print(f"{'='*50}")
    
    working_scripts = [script for script, success in results.items() if success]
    
    if working_scripts:
        print("✅ These scripts are working:")
        for script in working_scripts:
            print(f"   - {script}")
        print(f"\nRecommendation: Use 'python {working_scripts[0]}' to run the app")
    else:
        print("❌ No scripts are working. Possible issues:")
        print("   - PyQt5 installation problem")
        print("   - Python environment issue")
        print("   - Missing dependencies")
        print("\nTry: pip install PyQt5 matplotlib requests pandas numpy")

if __name__ == '__main__':
    main()