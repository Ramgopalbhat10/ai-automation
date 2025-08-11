"""Pytest adapter for YAML test suites with allure integration"""
import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any

import pytest
import allure
from allure_commons.types import AttachmentType

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.yaml_loader import YAMLLoader
from config.config import Config
from test_engine.test_engine import TestEngine
from test_engine.result_collector import ResultCollector, TestResult
from browser_manager import BrowserManager
from llm_integration.llm_provider import LLMProvider


def _extract_environment_from_path(yaml_file_path: str) -> str:
    """Extract environment information from YAML file path"""
    path_parts = Path(yaml_file_path).parts
    
    # Look for common environment indicators in path
    env_keywords = ['production', 'staging', 'development', 'dev', 'prod', 'test']
    for part in path_parts:
        if part.lower() in env_keywords:
            return part.lower()
    
    # Default to 'unknown' if no environment found
    return 'unknown'


class YamlTestSuiteAdapter:
    """Adapter to convert YAML test suites to pytest test cases"""
    
    def __init__(self, yaml_file_path: str):
        self.yaml_file_path = yaml_file_path
        self.test_suite = None
        self.test_engine = None
        self.result_collector = None
        
    def load_test_suite(self):
        """Load and validate YAML test suite"""
        self.test_suite = YAMLLoader.load_test_suite(self.yaml_file_path)
        return self.test_suite

    def setup_test_engine(self):
        """Initialize test engine components"""
        # Load configuration
        config = Config()
        
        # Set base_url from test suite into config if not already set
        if self.test_suite and self.test_suite.base_url and not config.get("base_url"):
            config.set("base_url", self.test_suite.base_url)
            print(f"🔗 Set base URL from test suite: {self.test_suite.base_url}")
        
        # Set LLM provider from test suite if specified
        if self.test_suite and self.test_suite.default_llm_provider:
            config.set("llm.provider", self.test_suite.default_llm_provider)
            print(f"🧠 Set LLM provider from test suite: {self.test_suite.default_llm_provider}")
        
        # Initialize test engine with config
        self.test_engine = TestEngine(config)
        self.result_collector = self.test_engine.result_collector
        
        # Set test suite info for reporting
        if self.test_suite:
            self.result_collector.set_test_suite_info(
                test_suite_name=self.test_suite.name,
                test_suite_description=self.test_suite.description,
                base_url=self.test_suite.base_url,
                total_tests=len(self.test_suite.tests)
            )

    async def execute_test_case(self, test_case) -> TestResult:
        """Execute a single test case and return results"""
        test_name = test_case.name
        
        with allure.step(f"Executing test case: {test_name}"):
            # Add test case details to allure
            allure.dynamic.title(test_name)
            allure.dynamic.description(test_case.description or '')
            
            # Add test case metadata
            if hasattr(test_case, 'tags') and test_case.tags:
                for tag in test_case.tags:
                    allure.dynamic.tag(tag)
            
            # Add test case specific information
            if hasattr(test_case, 'url') and test_case.url:
                allure.dynamic.tag(f"url:{test_case.url}")
            
            if hasattr(test_case, 'timeout') and test_case.timeout:
                allure.dynamic.tag(f"timeout:{test_case.timeout}s")
            
            # Add test case prompt as attachment for debugging
            if hasattr(test_case, 'prompt') and test_case.prompt:
                allure.attach(
                    test_case.prompt,
                    name="Test Case Prompt",
                    attachment_type=AttachmentType.TEXT
                )
            
            # Execute the test case
            result = await self.test_engine.execute_single_test(test_case)
            
            # Attach screenshots if available
            if result.screenshots:
                for i, screenshot in enumerate(result.screenshots):
                    if os.path.exists(screenshot):
                        with open(screenshot, 'rb') as f:
                            allure.attach(
                                f.read(),
                                name=f"Screenshot_{i+1}",
                                attachment_type=AttachmentType.PNG
                            )
            
            # Attach logs if available
            if result.output:
                allure.attach(
                    result.output,
                    name="Test Output",
                    attachment_type=AttachmentType.TEXT
                )
            
            return result


class StableYamlParam:
    """Stable wrapper to make pytest param representation deterministic for Allure history"""
    def __init__(self, adapter: YamlTestSuiteAdapter, case):
        self.adapter = adapter
        self.case = case
    
    def __repr__(self) -> str:
        # Only return test case name for stable param id string
        return f"{self.case.name}"
    
    __str__ = __repr__


def pytest_generate_tests(metafunc):
    """Dynamically generate test cases from YAML files"""
    if "yaml_test_case" in metafunc.fixturenames:
        # Get YAML file path from pytest command line or environment
        yaml_file = metafunc.config.getoption("--yaml-suite", default=None)
        
        if not yaml_file:
            # Look for YAML_SUITE environment variable
            yaml_file = os.environ.get("YAML_SUITE")
        
        if not yaml_file:
            # Default to production test suite
            yaml_file = "test_suites/production/mrgb_blog_test_suite.yaml"
        
        # Convert to absolute path
        if not os.path.isabs(yaml_file):
            yaml_file = os.path.join(project_root, yaml_file)
        
        if not os.path.exists(yaml_file):
            pytest.skip(f"YAML test suite file not found: {yaml_file}")
            return
        
        # Load test suite
        adapter = YamlTestSuiteAdapter(yaml_file)
        test_suite = adapter.load_test_suite()
        
        if not test_suite or not hasattr(test_suite, 'tests') or not test_suite.tests:
            pytest.skip(f"No test cases found in YAML file: {yaml_file}")
            return
        
        # Generate test parameters with suite information
        test_cases = test_suite.tests
        suite_name = test_suite.name if test_suite.name else Path(yaml_file).stem
        environment = _extract_environment_from_path(yaml_file)
        
        # Create stable test IDs for consistent Allure historyId
        # Use only the test case name to ensure consistency across runs
        test_ids = [case.name for case in test_cases]
        
        metafunc.parametrize(
            "yaml_test_case",
            [StableYamlParam(adapter, case) for case in test_cases],
            ids=test_ids
        )


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
@pytest.mark.browser
@pytest.mark.yaml_suite
async def test_yaml_test_case(yaml_test_case):
    """Execute a YAML test case"""
    param: StableYamlParam = yaml_test_case
    adapter, test_case = param.adapter, param.case
    
    # Setup test engine
    adapter.setup_test_engine()
    
    # Extract suite information for better categorization
    suite_name = adapter.test_suite.name if adapter.test_suite else "Unknown Suite"
    suite_description = adapter.test_suite.description if adapter.test_suite else ""
    base_url = adapter.test_suite.base_url if adapter.test_suite else ""
    
    # Add stable allure metadata for consistent historyId
    environment = _extract_environment_from_path(adapter.yaml_file_path)
    
    # Use stable hierarchy for consistent historyId
    allure.dynamic.parent_suite(f"{environment.title()} Environment")
    allure.dynamic.suite(suite_name)
    allure.dynamic.sub_suite("Test Cases")  # Static sub-suite name
    
    # Use static categorization
    allure.dynamic.epic(suite_name)
    allure.dynamic.feature("YAML Test Suite")  # Static feature name
    allure.dynamic.story(test_case.name)
    allure.dynamic.title(test_case.name)  # Simple, stable title
    
    # Add description without dynamic elements
    if test_case.description:
        allure.dynamic.description(test_case.description)
    
    # Add static tags that don't change between runs
    if base_url:
        allure.dynamic.tag("web-test")
    
    allure.dynamic.tag(f"suite:{Path(adapter.yaml_file_path).stem}")
    allure.dynamic.tag(f"environment:{environment}")
    
    # Execute test case
    result = await adapter.execute_test_case(test_case)
    
    # Assert test success
    assert result.status == 'passed', f"Test case failed: {result.error_message or 'Unknown error'}"
    
    # Add comprehensive result summary to allure
    allure.attach(
        f"Test Suite: {suite_name}\n"
        f"Test Case: {test_case.name}\n"
        f"Base URL: {base_url}\n"
        f"Test Duration: {result.duration:.2f}s\n"
        f"Status: {result.status.upper()}\n"
        f"Start Time: {result.start_time}\n"
        f"End Time: {result.end_time}",
        name="Test Execution Summary",
        attachment_type=AttachmentType.TEXT
    )


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--yaml-suite",
        action="store",
        default=None,
        help="Path to YAML test suite file"
    )


def pytest_configure(config):
    """Configure pytest with custom markers and settings"""
    config.addinivalue_line(
        "markers", "yaml_suite: mark test as a YAML test suite test"
    )
    config.addinivalue_line(
        "markers", "browser: mark test as a browser automation test"
    )