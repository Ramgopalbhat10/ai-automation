#!/usr/bin/env python3
"""
End-to-End Amazon Test Suite Runner

This script demonstrates the complete BrowserTest AI framework by running
a comprehensive test suite against Amazon's website without requiring login.

Usage:
    python scripts/test_amazon_e2e.py
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import Config
from test_engine.test_engine import TestEngine
from test_engine.test_runner import TestRunner
from test_engine.result_collector import ResultCollector
from llm_integration.llm_provider import LLMProvider
from browser_manager.browser_manager import BrowserManager

def print_banner():
    """Print a nice banner for the test run"""
    print("\n" + "="*80)
    print("🚀 BrowserTest AI - Amazon End-to-End Test Suite")
    print("="*80)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Target: Amazon.com (Basic functionality without login)")
    print(f"🧠 LLM: Google Gemini with Vision Support")
    print(f"🌍 Browser: Chrome (Non-headless for visibility)")
    print("="*80 + "\n")

def print_test_summary(results):
    """Print a summary of test results"""
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.status == 'passed')
    failed_tests = sum(1 for r in results if r.status == 'failed')
    
    print("\n" + "="*80)
    print("📊 TEST EXECUTION SUMMARY")
    print("="*80)
    print(f"📈 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "📊 Success Rate: 0%")
    
    if failed_tests > 0:
        print("\n❌ FAILED TESTS:")
        for result in results:
            if result.status == 'failed':
                print(f"   • {result.test_name}: {result.error_message}")
    
    print("\n✅ PASSED TESTS:")
    for result in results:
        if result.status == 'passed':
            duration = (result.end_time - result.start_time).total_seconds()
            print(f"   • {result.test_name} ({duration:.1f}s)")
    
    print("="*80)

async def main():
    """Main test execution function"""
    print_banner()
    
    try:
        # Initialize configuration
        print("🔧 Initializing configuration...")
        config = Config()
        
        # Load the Amazon test suite
        test_suite_path = project_root / "test_suites" / "examples" / "amazon_test_suite.yaml"
        if not test_suite_path.exists():
            raise FileNotFoundError(f"Test suite not found: {test_suite_path}")
        
        print(f"📋 Loading test suite: {test_suite_path}")
        
        # Initialize LLM provider
        print("🧠 Initializing LLM provider (Groq)...")
        llm_provider = LLMProvider.create_provider(
            provider_type="groq",
            config=config
        )
        
        # Test LLM connection
        print("🔗 Testing LLM connection...")
        if not llm_provider.test_connection():
            raise Exception("Failed to connect to LLM provider")
        print("✅ LLM connection successful")
        
        # Initialize browser manager
        print("🌐 Initializing browser manager...")
        browser_manager = BrowserManager(config)
        
        # Initialize test engine
        print("⚙️ Initializing test engine...")
        test_engine = TestEngine(config)
        
        # Initialize result collector
        print("📊 Initializing result collector...")
        result_collector = ResultCollector()
        
        # Load and validate test suite
        print("📖 Loading and validating test suite...")
        from config.yaml_loader import YAMLLoader
        yaml_loader = YAMLLoader()
        test_suite = yaml_loader.load_test_suite(str(test_suite_path))
        print(f"✅ Loaded {len(test_suite.tests)} tests")
        
        # Display test overview
        print("\n📋 TEST SUITE OVERVIEW:")
        print(f"   Name: {test_suite.name}")
        print(f"   Description: {test_suite.description}")
        print(f"   Base URL: {test_suite.base_url}")
        print(f"   Tests: {len(test_suite.tests)}")
        
        print("\n🧪 TESTS TO EXECUTE:")
        for i, test in enumerate(test_suite.tests, 1):
            tags_str = ", ".join(test.tags) if test.tags else "no tags"
            print(f"   {i:2d}. {test.name} ({tags_str})")
        
        # Auto-proceed with test execution
        print("\n⚠️  IMPORTANT: This will open a browser and navigate to Amazon.com")
        print("   Make sure you have a stable internet connection.")
        print("\n✅ Auto-proceeding with test execution...")
        
        print("\n🚀 Starting test execution...")
        print("-" * 80)
        
        # Execute the test suite
        summary = await test_engine.execute_test_suite(test_suite)
        
        # Get results from test engine
        print("\n💾 Collecting and saving results...")
        results = test_engine.get_results()
        for result in results:
            result_collector.add_result(result)
        
        # Generate reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = project_root / "reports"
        report_dir.mkdir(exist_ok=True)
        
        html_report_path = report_dir / f"amazon_test_report_{timestamp}.html"
        json_report_path = report_dir / f"amazon_test_report_{timestamp}.json"
        
        html_path = result_collector.export_to_html(str(html_report_path))
        json_path = result_collector.export_to_json(str(json_report_path))
        
        print(f"📄 HTML report generated: {html_path}")
        print(f"📄 JSON report generated: {json_path}")
        report_path = html_path  # For backward compatibility
        
        # Print summary
        print_test_summary(results)
        
        # Final status
        failed_count = sum(1 for r in results if r.status == 'failed')
        if failed_count == 0:
            print("\n🎉 ALL TESTS PASSED! The BrowserTest AI framework is working correctly.")
        else:
            print(f"\n⚠️  {failed_count} test(s) failed. Check the detailed report for more information.")
        
        print(f"\n📁 Detailed results available in: {report_path}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during test execution: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\n🧹 Cleaning up resources...")
        try:
            if 'browser_manager' in locals():
                await browser_manager.cleanup()
            print("✅ Cleanup completed")
        except Exception as e:
            print(f"⚠️  Warning during cleanup: {str(e)}")
        
        print("\n👋 Test execution completed.")
        print("="*80)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())