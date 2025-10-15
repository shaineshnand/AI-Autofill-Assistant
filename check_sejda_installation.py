#!/usr/bin/env python3
"""
Check if Sejda PDF Desktop is installed and accessible
"""

import subprocess
import os
from pathlib import Path

def check_sejda_installation():
    """Check if Sejda Desktop CLI is installed"""
    
    print("=" * 60)
    print("Sejda PDF Desktop Installation Checker")
    print("=" * 60)
    print()
    
    # Common paths to check
    common_paths = [
        # Windows
        r"C:\Program Files\Sejda PDF Desktop\sejda-console.exe",
        r"C:\Program Files (x86)\Sejda PDF Desktop\sejda-console.exe",
        r"C:\Program Files\Sejda\sejda-console.exe",
        r"C:\Program Files (x86)\Sejda\sejda-console.exe",
        # macOS
        "/Applications/Sejda PDF.app/Contents/MacOS/sejda-console",
        "/usr/local/bin/sejda-console",
        # Linux
        "/opt/sejda/sejda-console",
        "/usr/bin/sejda-console",
    ]
    
    # Check if sejda-console is in PATH
    print("1. Checking if sejda-console is in PATH...")
    try:
        result = subprocess.run(['sejda-console', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ FOUND in PATH!")
            print(f"   Version: {result.stdout.strip()}")
            print()
            print("🎉 Sejda Desktop CLI is ready to use!")
            print("   Your PDFs will be processed OFFLINE with best accuracy.")
            return True
    except FileNotFoundError:
        print("   ❌ Not found in PATH")
    except subprocess.TimeoutExpired:
        print("   ⚠️  Command timed out")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    print()
    print("2. Checking common installation paths...")
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"   ✅ FOUND: {path}")
            try:
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"   Version: {result.stdout.strip()}")
                    print()
                    print("🎉 Sejda Desktop CLI is installed!")
                    print(f"   Path: {path}")
                    print()
                    print("   To make it accessible from anywhere, add it to your PATH.")
                    return True
            except Exception as e:
                print(f"   ⚠️  Found but can't execute: {e}")
    
    print("   ❌ Not found in common paths")
    print()
    print("=" * 60)
    print("Sejda Desktop CLI NOT FOUND")
    print("=" * 60)
    print()
    print("📥 To install Sejda PDF Desktop:")
    print()
    print("1. Visit: https://www.sejda.com/desktop")
    print("2. Download Sejda PDF Desktop for your operating system")
    print("3. Install the application")
    print("4. Run this script again to verify")
    print()
    print("💡 Benefits of using Sejda:")
    print("   • Best accuracy for field detection")
    print("   • All processing done OFFLINE (no data sent online)")
    print("   • Automatically detects blank spaces and dotted lines")
    print()
    print("📝 Note:")
    print("   If Sejda is not installed, the system will use fallback")
    print("   detection methods (less accurate but still functional).")
    print()
    
    return False

if __name__ == "__main__":
    check_sejda_installation()



