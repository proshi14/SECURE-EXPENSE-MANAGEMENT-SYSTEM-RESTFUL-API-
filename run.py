#!/usr/bin/env python
"""
Expense Tracker - Application Launcher
This script starts the FastAPI server and automatically opens the browser.
"""

import subprocess
import sys
import os

def main():
    print("=" * 50)
    print("Starting Expense Tracker Application...")
    print("=" * 50)
    print("\nThe application will:")
    print("  ✓ Start the server at http://127.0.0.1:8000")
    print("  ✓ Automatically open your default browser")
    print("  ✓ Enable auto-reload for development\n")
    print("Press CTRL+C to stop the server\n")
    
    # Change to the script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run the FastAPI server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--reload",
            "--host", "127.0.0.1",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n\nApplication stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
