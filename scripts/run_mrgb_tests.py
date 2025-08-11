#!/usr/bin/env python3
"""
MRGB Blog Test Runner
Demonstrates running the production test suite for mrgb.in with multiple tabs support.

This script shows how the BrowserTest AI framework can handle multiple tabs
within the same browser instance for efficient testing.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config import Config
from config.yaml_loader import YAMLLoader
from llm_integration.llm_provider import LLMProvider
from llm_integration.browser_use_integration import BrowserUseIntegration
from test_engine.test_engine import TestEngine
from test_engine.result_collector import ResultCollector
from browser_use import BrowserSession, Agent
from playwright.async_api import async_playwright


class MRGBTestRunner:
    """Specialized test runner for MRGB blog site with multi-tab support"""
    
    def __init__(self, config_path: str = None):
        self.config = Config(config_path)
        self.llm_provider = LLMProvider.create_provider(self.config)
        self.browser_integration = BrowserUseIntegration(self.config, self.llm_provider)
        self.result_collector = ResultCollector()
        
    async def run_multi_tab_tests(self, test_suite_path: str) -> Dict[str, Any]:
        """
        Run tests with multiple tabs in the same browser instance.
        This demonstrates the browser-use library's capability to handle
        multiple tabs efficiently.
        """
        print(f"Loading test suite: {test_suite_path}")
        
        # Load test suite configuration
        yaml_loader = YAMLLoader()
        test_suite = yaml_loader.load_test_suite(test_suite_path)
        
        print(f"Test Suite: {test_suite['name']}")
        print(f"Description: {test_suite['description']}")
        print(f"Base URL: {test_suite['base_url']}")
        print(f"Number of tests: {len(test_suite['tests'])}")
        print("\n" + "="*60 + "\n")
        
        # Initialize browser session with keep_alive for multi-tab support
        browser_session = BrowserSession(
            headless=test_suite.get('default_browser', {}).get('headless', False),
            viewport=test_suite.get('default_browser', {}).get('viewport', {'width': 1920, 'height': 1080}),
            keep_alive=True  # Keep browser alive for multiple tabs
        )
        
        try:
            await browser_session.start()
            print("✅ Browser session started successfully")
            
            # Run setup if specified
            if 'setup_prompt' in test_suite:
                print("🔧 Running setup...")
                await self._run_setup(browser_session, test_suite['setup_prompt'], test_suite['base_url'])
            
            # Determine execution strategy
            if test_suite.get('parallel', False):
                print("🚀 Running tests in parallel with multiple tabs")
                results = await self._run_parallel_tests(browser_session, test_suite)
            else:
                print("📋 Running tests sequentially with tab reuse")
                results = await self._run_sequential_tests(browser_session, test_suite)
            
            # Run teardown if specified
            if 'teardown_prompt' in test_suite:
                print("🧹 Running teardown...")
                await self._run_teardown(browser_session, test_suite['teardown_prompt'])
            
            return results
            
        finally:
            await browser_session.close()
            print("🔒 Browser session closed")
    
    async def _run_setup(self, browser_session: BrowserSession, setup_prompt: str, base_url: str):
        """Run setup tasks"""
        llm = await self.llm_provider.get_llm()
        agent = Agent(
            task=setup_prompt,
            llm=llm,
            browser_session=browser_session
        )
        
        # Navigate to base URL first
        page = await browser_session.get_current_page()
        await page.goto(base_url)
        
        result = await agent.run()
        print(f"   Setup completed: {result}")
    
    async def _run_teardown(self, browser_session: BrowserSession, teardown_prompt: str):
        """Run teardown tasks"""
        llm = await self.llm_provider.get_llm()
        agent = Agent(
            task=teardown_prompt,
            llm=llm,
            browser_session=browser_session
        )
        result = await agent.run()
        print(f"   Teardown completed: {result}")
    
    async def _run_parallel_tests(self, browser_session: BrowserSession, test_suite: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Run tests in parallel using multiple tabs.
        Each test gets its own tab in the same browser instance.
        """
        tests = test_suite['tests']
        base_url = test_suite['base_url']
        
        # Create agents for parallel execution
        agents = []
        for test in tests:
            # Create a new page (tab) for each test
            new_page = await browser_session.browser_context.new_page()
            
            # Navigate to the test URL
            test_url = base_url + test.get('url', '/')
            await new_page.goto(test_url)
            
            # Create agent with the specific page
            llm = await self.llm_provider.get_llm()
            agent = Agent(
                task=test['prompt'],
                llm=llm,
                page=new_page
            )
            
            agents.append((agent, test))
        
        # Run all agents in parallel
        print(f"🔄 Executing {len(agents)} tests in parallel...")
        tasks = [self._execute_test_with_agent(agent, test) for agent, test in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def _run_sequential_tests(self, browser_session: BrowserSession, test_suite: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Run tests sequentially, reusing tabs when possible.
        This approach is more resource-efficient for smaller test suites.
        """
        tests = test_suite['tests']
        base_url = test_suite['base_url']
        results = []
        
        for i, test in enumerate(tests):
            print(f"\n📝 Running test {i+1}/{len(tests)}: {test['name']}")
            
            # For sequential tests, we can reuse the main page or create new tabs as needed
            if test.get('tags', []) and 'multi-tab' in test['tags']:
                # For multi-tab tests, create a new tab
                new_page = await browser_session.browser_context.new_page()
                test_url = base_url + test.get('url', '/')
                await new_page.goto(test_url)
                
                llm = await self.llm_provider.get_llm()
                agent = Agent(
                    task=test['prompt'],
                    llm=llm,
                    page=new_page
                )
            else:
                # Use the main browser session
                test_url = base_url + test.get('url', '/')
                page = await browser_session.get_current_page()
                await page.goto(test_url)
                
                llm = await self.llm_provider.get_llm()
                agent = Agent(
                    task=test['prompt'],
                    llm=llm,
                    browser_session=browser_session
                )
            
            result = await self._execute_test_with_agent(agent, test)
            results.append(result)
        
        return results
    
    async def _execute_test_with_agent(self, agent: Agent, test: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single test with the given agent.
        """
        test_name = test['name']
        print(f"   🔍 Executing: {test_name}")
        
        try:
            # Run the agent
            result = await agent.run()
            
            # Collect test result
            test_result = {
                'name': test_name,
                'status': 'passed',
                'result': result,
                'description': test.get('description', ''),
                'tags': test.get('tags', []),
                'success_criteria': test.get('success_criteria', '')
            }
            
            print(f"   ✅ {test_name}: PASSED")
            return test_result
            
        except Exception as e:
            test_result = {
                'name': test_name,
                'status': 'failed',
                'error': str(e),
                'description': test.get('description', ''),
                'tags': test.get('tags', []),
                'success_criteria': test.get('success_criteria', '')
            }
            
            print(f"   ❌ {test_name}: FAILED - {str(e)}")
            return test_result


async def main():
    """Main execution function"""
    print("🚀 MRGB Blog Test Runner")
    print("Testing https://mrgb.in with multi-tab browser automation\n")
    
    # Path to the test suite
    test_suite_path = project_root / "test_suites" / "production" / "mrgb_blog_test_suite.yaml"
    
    if not test_suite_path.exists():
        print(f"❌ Test suite not found: {test_suite_path}")
        return
    
    # Initialize and run tests
    runner = MRGBTestRunner()
    
    try:
        results = await runner.run_multi_tab_tests(str(test_suite_path))
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST EXECUTION SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'passed')
        failed = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'failed')
        errors = sum(1 for r in results if isinstance(r, Exception))
        
        print(f"Total Tests: {len(results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Errors: {errors}")
        
        if failed > 0 or errors > 0:
            print("\n🔍 Failed Tests:")
            for result in results:
                if isinstance(result, dict) and result.get('status') == 'failed':
                    print(f"   - {result['name']}: {result.get('error', 'Unknown error')}")
                elif isinstance(result, Exception):
                    print(f"   - Exception: {str(result)}")
        
        print("\n🎉 Test execution completed!")
        
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Ensure we have the required environment variables
    if not os.getenv('GOOGLE_API_KEY') and not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: No LLM API key found. Please set GOOGLE_API_KEY or OPENAI_API_KEY")
        print("   You can set it in your environment or .env file")
    
    asyncio.run(main())