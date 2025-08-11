#!/usr/bin/env python3
"""Simple test script to verify browser automation is working"""

import asyncio
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from config.config import Config
from config.yaml_loader import TestCase, BrowserConfig
from test_engine.test_engine import TestEngine
from llm_integration.llm_provider import LLMProvider
from browser_manager import BrowserManager

async def test_simple_automation():
    """Test simple browser automation"""
    print("🔧 Initializing test components...")
    
    # Initialize configuration
    config = Config()
    
    # Check if we have API keys
    google_key = config.get("llm.google_api_key")
    openai_key = config.get("llm.openai_api_key")
    
    if not google_key and not openai_key:
        print("❌ No API keys found. Please set GOOGLE_API_KEY or OPENAI_API_KEY environment variable.")
        return
    
    # Use Google if available, otherwise OpenAI
    if google_key:
        config._config["llm"]["provider"] = "google"
        print("🤖 Using Google Gemini provider")
    else:
        config._config["llm"]["provider"] = "openai"
        print("🤖 Using OpenAI provider")
    
    # Initialize test engine
    test_engine = TestEngine(config)
    
    # Create a simple test case for Google
    test_case = TestCase(
        name="Google Search Test",
        description="Test Google homepage loads and search works",
        prompt="Go to Google homepage and verify it loads correctly. Look for the Google logo and search box.",
        url="https://www.google.com",
        success_criteria="Page loads successfully and Google logo is visible",
        timeout=60,
        retry_count=1,
        browser=BrowserConfig(headless=False)  # Show browser for demo
    )
    
    print(f"🚀 Running test: {test_case.name}")
    print(f"📝 Description: {test_case.description}")
    print(f"🌐 URL: {test_case.url}")
    print(f"🎯 Prompt: {test_case.prompt}")
    
    try:
        result = await test_engine.execute_single_test(test_case)
        
        print(f"\n✅ Test completed!")
        print(f"📊 Status: {result.status}")
        print(f"⏱️ Duration: {result.duration:.2f} seconds")
        print(f"📝 Output: {result.output[:300]}..." if len(result.output) > 300 else f"📝 Output: {result.output}")
        
        if result.error_message:
            print(f"❌ Error: {result.error_message}")
        
        if result.screenshots:
            print(f"📸 Screenshots: {len(result.screenshots)} captured")
            for i, screenshot in enumerate(result.screenshots):
                print(f"   📷 Screenshot {i+1}: {screenshot}")
        
        return result.status == "passed"
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 BrowserTest AI - Simple Automation Test")
    print("=" * 50)
    success = asyncio.run(test_simple_automation())
    if success:
        print("\n🎉 Browser automation is working correctly!")
    else:
        print("\n❌ Browser automation test failed.")