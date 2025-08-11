"""Main test execution engine for BrowserTest AI"""

import asyncio
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from config import Config
from config.yaml_loader import TestSuite, TestCase, YAMLLoader
from llm_integration.llm_provider import LLMProvider
from browser_manager import BrowserManager
from .test_runner import TestRunner
from .result_collector import ResultCollector, TestResult


class TestEngine:
    """Main test execution engine with LLM integration"""
    
    def __init__(self, config: Config):
        """Initialize test engine
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # Get LLM provider type from config
        provider_type = config.get("llm.provider", "google")
        self.llm_provider = LLMProvider.create_provider(provider_type, config)
        self.browser_manager = BrowserManager(config)
        self.result_collector = ResultCollector()
    
    async def execute_test_suite(self, test_suite: TestSuite) -> Dict[str, Any]:
        """Execute a complete test suite
        
        Args:
            test_suite: Test suite configuration
            
        Returns:
            Execution results summary
        """
        print(f"Starting test suite: {test_suite.name}")
        start_time = datetime.now()
        
        # Set test suite information in result collector
        self.result_collector.set_test_suite_info(
            test_suite_name=test_suite.name,
            test_suite_description=test_suite.description,
            base_url=test_suite.base_url,
            total_tests=len(test_suite.tests)
        )
        
        # Setup phase
        if test_suite.setup_prompt:
            await self._execute_setup(test_suite.setup_prompt)
        
        # Execute tests - check for config overrides
        # Config overrides take precedence over YAML settings
        parallel_execution = self.config.get("test.parallel", test_suite.parallel)
        max_workers = self.config.get("test.max_workers", test_suite.max_workers)
        
        if parallel_execution:
            results = await self._execute_tests_parallel(
                test_suite.tests, 
                max_workers
            )
        else:
            results = await self._execute_tests_sequential(test_suite.tests)
        
        # Teardown phase
        if test_suite.teardown_prompt:
            await self._execute_teardown(test_suite.teardown_prompt)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Collect and return results
        summary = self.result_collector.generate_summary(
            test_suite.name,
            results,
            duration
        )
        
        # Add LLM information to summary
        summary["llm_info"] = self.llm_provider.get_model_info()
        
        print(f"Test suite completed in {duration:.2f} seconds")
        return summary
    

    
    async def execute_single_test(self, test_case: TestCase) -> TestResult:
        """Execute a single test case with LLM-powered automation
        
        Args:
            test_case: Test case configuration
            
        Returns:
            Test execution result
        """
        test_runner = TestRunner(
            self.config,
            self.llm_provider,
            self.browser_manager
        )
        
        return await test_runner.run_test(test_case)
    
    async def _execute_tests_sequential(self, test_cases: List[TestCase]) -> List[TestResult]:
        """Execute tests sequentially
        
        Args:
            test_cases: List of test cases
            
        Returns:
            List of test results
        """
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"Executing test {i}/{len(test_cases)}: {test_case.name}")
            result = await self.execute_single_test(test_case)
            results.append(result)
            self.result_collector.add_result(result)
        
        return results
    
    async def _execute_tests_parallel(self, test_cases: List[TestCase], max_workers: int) -> List[TestResult]:
        """Execute tests in parallel
        
        Args:
            test_cases: List of test cases
            max_workers: Maximum number of parallel workers
            
        Returns:
            List of test results
        """
        semaphore = asyncio.Semaphore(max_workers)
        
        async def run_with_semaphore(test_case: TestCase) -> TestResult:
            async with semaphore:
                print(f"Executing test: {test_case.name}")
                result = await self.execute_single_test(test_case)
                self.result_collector.add_result(result)
                return result
        
        # Create tasks for all test cases
        tasks = [run_with_semaphore(test_case) for test_case in test_cases]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create failed result for exception
                failed_result = TestResult(
                    test_name=test_cases[i].name,
                    status="failed",
                    error_message=str(result),
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration=0.0
                )
                processed_results.append(failed_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_setup(self, setup_prompt: str):
        """Execute test suite setup
        
        Args:
            setup_prompt: Natural language setup instructions
        """
        if not setup_prompt:
            return
        
        print("Executing test suite setup...")
        print(f"Setup task: {setup_prompt}")
        
        # For now, we'll just log the setup prompt
        # In a full implementation, this could execute the setup using the LLM
        # TODO: Implement setup execution using browser-use agent
    
    async def _execute_teardown(self, teardown_prompt: str):
        """Execute test suite teardown
        
        Args:
            teardown_prompt: Natural language teardown instructions
        """
        if not teardown_prompt:
            return
        
        print("Executing test suite teardown...")
        print(f"Teardown task: {teardown_prompt}")
        
        # For now, we'll just log the teardown prompt
        # In a full implementation, this could execute the teardown using the LLM
        # TODO: Implement teardown execution using browser-use agent
    
    def get_results(self) -> List[TestResult]:
        """Get all test results
        
        Returns:
            List of all test results
        """
        return self.result_collector.get_all_results()
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.browser_manager.cleanup()
    
    def get_llm_info(self) -> Dict[str, Any]:
        """Get LLM provider information
        
        Returns:
            LLM provider details
        """
        return self.llm_provider.get_model_info()