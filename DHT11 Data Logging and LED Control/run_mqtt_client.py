#!/usr/bin/env python3
"""
DHT11 Data Logging and LED Control - Alternative launcher
This script helps resolve import issues by explicitly setting Python path
"""

import sys
import os

# Add the miniforge site-packages to Python path
sys.path.insert(0, "/home/titan/miniforge3/lib/python3.12/site-packages")

# Change to project directory
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)

# Now import and run the main script
try:
    print("🔄 Loading DHT11 MQTT Client...")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python executable: {sys.executable}")
    print(f"📦 Python path includes: {sys.path[0]}")
    print()

    # Import the main module
    sys.path.insert(0, os.path.join(project_dir, "src"))

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Trying alternative import method...")

    # Alternative: Execute the script directly
    import subprocess

    result = subprocess.run(
        [
            "/home/titan/miniforge3/bin/python3",
            os.path.join(project_dir, "src", "pubsub.py"),
        ]
    )
    sys.exit(result.returncode)

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
