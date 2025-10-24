#!/usr/bin/env python3
"""
Sejda PDF Integration Setup Script

This script helps set up Sejda PDF SDK for use with our AI Autofill Assistant.
It downloads the Sejda SDK JAR file and sets up the necessary configuration.

Usage:
    python setup_sejda.py

Requirements:
    - Java 8 or higher
    - Internet connection for downloading Sejda SDK
"""

import os
import sys
import urllib.request
import subprocess
import shutil
from pathlib import Path

SEJDA_VERSION = "3.2.86"
# Try multiple possible download URLs
SEJDA_JAR_URLS = [
    f"https://github.com/torakiki/sejda/releases/download/v{SEJDA_VERSION}/sejda-console-{SEJDA_VERSION}.jar",
    f"https://github.com/torakiki/sejda/releases/download/sejda-{SEJDA_VERSION}/sejda-console-{SEJDA_VERSION}.jar",
    f"https://repo1.maven.org/maven2/org/sejda/sejda-console/{SEJDA_VERSION}/sejda-console-{SEJDA_VERSION}.jar"
]
SEJDA_JAR_NAME = f"sejda-console-{SEJDA_VERSION}.jar"

def check_java():
    """Check if Java is installed and get version"""
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stderr.split('\n')[0]
            print(f"✓ Java found: {version_line}")
            return True
        else:
            print("✗ Java not found")
            return False
    except FileNotFoundError:
        print("✗ Java not found. Please install Java 8 or higher.")
        return False

def download_sejda_jar():
    """Download Sejda SDK JAR file"""
    jar_path = Path(SEJDA_JAR_NAME)
    
    if jar_path.exists():
        print(f"✓ Sejda JAR already exists: {jar_path}")
        return str(jar_path)
    
    print(f"Downloading Sejda SDK {SEJDA_VERSION}...")
    
    # Try multiple download URLs
    for i, url in enumerate(SEJDA_JAR_URLS):
        try:
            print(f"  Trying URL {i+1}/{len(SEJDA_JAR_URLS)}: {url}")
            urllib.request.urlretrieve(url, SEJDA_JAR_NAME)
            print(f"✓ Downloaded: {SEJDA_JAR_NAME}")
            return str(jar_path)
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            continue
    
    print(f"✗ All download attempts failed")
    return None

def test_sejda_jar(jar_path):
    """Test if Sejda JAR works"""
    print("Testing Sejda SDK...")
    try:
        result = subprocess.run(['java', '-jar', jar_path, '--help'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ Sejda SDK is working correctly")
            return True
        else:
            print(f"✗ Sejda SDK test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Sejda SDK test timed out")
        return False
    except Exception as e:
        print(f"✗ Sejda SDK test failed: {e}")
        return False

def create_config_file():
    """Create a configuration file for Sejda integration"""
    config_content = """# Sejda PDF Integration Configuration
# This file contains settings for the Sejda PDF integration

[sejda]
# Path to Sejda SDK JAR file
jar_path = sejda-console-3.2.86.jar

# Sejda Desktop executable path (optional)
desktop_path = 

# Field detection settings
min_field_width = 30
min_field_height = 15
detect_blanks = true
detect_dotted_lines = true

# Output settings
output_format = pdf
compress_output = true
"""
    
    config_path = "sejda_config.ini"
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"✓ Created configuration file: {config_path}")
    return config_path

def main():
    """Main setup function"""
    print("=== Sejda PDF Integration Setup ===")
    print()
    
    # Check Java
    if not check_java():
        print("\nPlease install Java 8 or higher and try again.")
        print("Download from: https://www.oracle.com/java/technologies/downloads/")
        return False
    
    print()
    
    # Download Sejda JAR
    jar_path = download_sejda_jar()
    if not jar_path:
        return False
    
    print()
    
    # Test Sejda JAR
    if not test_sejda_jar(jar_path):
        return False
    
    print()
    
    # Create config file
    create_config_file()
    
    print()
    print("=== Setup Complete! ===")
    print()
    print("Sejda PDF integration is now ready to use.")
    print("You can now use the '/upload-sejda/' endpoint for better PDF field detection.")
    print()
    print("Next steps:")
    print("1. Restart your Django server")
    print("2. Use the new Sejda integration endpoint for PDF uploads")
    print("3. Enjoy more accurate field detection!")
    print()
    print("Alternative: If Sejda SDK doesn't work, you can:")
    print("1. Download Sejda PDF Desktop from: https://www.sejda.com/desktop")
    print("2. Install it and the system will try to use it automatically")
    print("3. Or use the enhanced visual detection we implemented earlier")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
