#!/usr/bin/env python3
"""
Example: Test windsurf.com blog for Wave 11 articles

This is a simple example showing how to use the website tester
to check if windsurf.com blog has articles about "Wave 11".
"""

import asyncio
import os
from dotenv import load_dotenv
from website_tester import WebsiteTester

async def test_windsurf_wave11():
    """Test windsurf.com for Wave 11 articles."""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if Google API key is available
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
        print("\nPlease create a .env file with your Google API key:")
        print("GOOGLE_API_KEY=your_api_key_here")
        print("\nOr set it as an environment variable.")
        return
    
    print("Testing windsurf.com blog for Wave 11 articles...")
    print("=" * 50)
    
    print("🤖 Initializing Website Tester with Google Gemini...")
    
    # Initialize the website tester
    tester = WebsiteTester(headless=False)
    
    try:
        # Test windsurf.com blog for Wave 11 content
        result = await tester.test_windsurf_blog("Wave 11")
        
        print("\nTest Results:")
        print("-" * 30)
        print(result)
        
    except Exception as e:
        print(f"Error during testing: {e}")
        print("\nTo get started:")
        print("1. Make sure you have installed all dependencies: pip install -r ../requirements.txt")
        print("2. Install Playwright browsers: playwright install")
        print("3. Check your Google API key is valid")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_windsurf_wave11())