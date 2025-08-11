#!/usr/bin/env python3
"""Test script to verify MRGB site automation with correct URL"""

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

async def test_mrgb_site():
    """Test MRGB site automation"""
    print("🔧 Initializing test components for MRGB site...")
    
    # Initialize configuration
    config = Config()
    
    # Check if we have OpenAI API key
    openai_key = config.get("llm.openai_api_key")
    
    if not openai_key:
        print("❌ No OpenAI API key found. Please set OPENAI_API_KEY environment variable.")
        return
    
    # Force use of OpenAI provider
    config._config["llm"]["provider"] = "openai"
    print("🤖 Using OpenAI provider (as requested)")
    
    # Initialize test engine
    test_engine = TestEngine(config)
    
    # Create a test case for MRGB site (the correct URL)
    test_case = TestCase(
        name="MRGB Homepage Test",
        description="Test MRGB homepage loads and displays key elements",
        prompt="Go to https://mrgb.in and verify the homepage loads correctly. Look for the site title 'MRGB', the greeting 'Hi, I'm Ram', and navigation links for 'blog' and 'work'.",
        url="https://mrgb.in",
        success_criteria="Page loads successfully and key elements are visible",
        timeout=120,
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
    print("🧪 BrowserTest AI - MRGB Site Test")
    print("=" * 50)
    print("📍 Testing the correct URL: https://mrgb.in")
    print("📍 Note: mrgb.io does not exist (DNS resolution fails)")
    print("📍 The test suite is correctly configured for mrgb.in")
    print("=" * 50)
    success = asyncio.run(test_mrgb_site())
    if success:
        print("\n🎉 MRGB site automation is working correctly!")
    else:
        print("\n❌ MRGB site automation test failed.")