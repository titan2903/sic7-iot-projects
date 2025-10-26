#!/usr/bin/env python3
"""
Run the DHT22 data logger from project root directory
This ensures correct CSV file path resolution
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import and run the main function
from logging_data import main

if __name__ == "__main__":
    print("🌡️  DHT22 Data Logger")
    print("📁 Working directory:", os.getcwd())
    print("📂 CSV will be saved to: data/dht22_data.csv")
    print("-" * 50)

    main()
