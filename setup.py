#!/usr/bin/env python3
"""
Setup script for Website Testing Automation

This script helps you set up the environment and test the installation.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_virtual_environment():
    """Check if virtual environment exists."""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment found")
        return True
    else:
        print("❌ Virtual environment not found")
        print("Please create one with: python -m venv venv")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import browser_use
        import langchain_openai
        import playwright
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install with: pip install -r requirements.txt")
        return False

def check_playwright_browsers():
    """Check if Playwright browsers are installed."""
    try:
        result = subprocess.run(["playwright", "install", "--dry-run"], 
                              capture_output=True, text=True)
        if "is already installed" in result.stdout or result.returncode == 0:
            print("✅ Playwright browsers are installed")
            return True
        else:
            print("❌ Playwright browsers not installed")
            print("Please install with: playwright install")
            return False
    except FileNotFoundError:
        print("❌ Playwright not found")
        return False

def check_api_key():
    """Check if Google API key is configured."""
    api_key = os.environ.get('GOOGLE_API_KEY')
    if api_key:
        print("✅ Google API key found in environment")
        return True
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'GOOGLE_API_KEY=' in content and 'your_google_api_key_here' not in content:
                print("✅ Google API key found in .env file")
                return True
    
    print("❌ Google API key not configured")
    print("Please set GOOGLE_API_KEY environment variable or create .env file")
    return False

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ .env file created. Please edit it with your API key.")
        return True
    return False

def main():
    """Main setup check function."""
    print("Website Testing Automation - Setup Check")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_virtual_environment(),
        check_dependencies(),
        check_playwright_browsers(),
        check_api_key()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 Setup complete! You're ready to run the automation scripts.")
        print("\nTry running:")
        print("  python example_windsurf_test.py")
        print("  python website_tester.py")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        
        # Try to create .env file if it doesn't exist
        create_env_file()
        
        print("\nSetup steps:")
        print("1. Create virtual environment: python -m venv venv")
        print("2. Activate virtual environment: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Mac/Linux)")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Install browsers: playwright install")
        print("5. Set up Google API key in .env file")
        print("\n📝 To set up your Google API key:")
        print("   1. Get an API key from https://aistudio.google.com/app/apikey")
        print("   2. Add it to your .env file: GOOGLE_API_KEY=your_key_here")

if __name__ == "__main__":
    main()