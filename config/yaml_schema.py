#!/usr/bin/env python3
"""Simplified YAML schema for prompt-based browser testing"""

import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class BrowserType(Enum):
    """Supported browser types"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
    CHROME = "chrome"
    EDGE = "edge"





@dataclass
class BrowserConfig:
    """Browser configuration for test execution"""
    type: BrowserType = BrowserType.CHROMIUM
    headless: bool = True
    viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    timeout: int = 30000
    slow_mo: int = 0
    args: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = BrowserType(self.type)


@dataclass
class TestCase:
    """Simplified test case with natural language prompts"""
    name: str
    prompt: str  # Natural language description of what to test
    success_criteria: str = ""  # Natural language success conditions
    
    # Basic configuration
    description: str = ""
    url: str = ""
    timeout: int = 120  # seconds (2 minutes)
    retry_count: int = 1
    tags: List[str] = field(default_factory=list)
    environment: str = "production"  # Environment identifier (dev, staging, production)
    
    # Browser configuration
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    
    # LLM settings
    llm_provider: Optional[str] = None  # google, openai, groq
    llm_model: Optional[str] = None
    llm_temperature: float = 0.1
    max_actions: int = 50
    
    # Data and variables
    variables: Dict[str, Any] = field(default_factory=dict)
    data_file: Optional[str] = None
    
    # Optional setup/teardown prompts
    setup_prompt: str = ""
    teardown_prompt: str = ""
    
    def __post_init__(self):
        pass


@dataclass
class TestSuite:
    """Test suite containing multiple test cases"""
    name: str
    description: str
    tests: List[TestCase]
    
    # Execution settings
    parallel: bool = False
    max_workers: int = 2
    fail_fast: bool = False
    
    # Default configurations
    default_browser: BrowserConfig = field(default_factory=BrowserConfig)
    default_llm_provider: str = "google"  # google, openai, groq
    default_llm_model: Optional[str] = None
    base_url: str = ""
    
    # Global setup/teardown
    setup_prompt: str = ""
    teardown_prompt: str = ""
    
    # Data management
    variables: Dict[str, Any] = field(default_factory=dict)
    data_sources: Dict[str, str] = field(default_factory=dict)
    
    # Reporting
    report_format: List[str] = field(default_factory=lambda: ["html", "json"])
    output_dir: str = "reports"
    
    def __post_init__(self):
        pass


class YAMLSchemaValidator:
    """Validator for simplified YAML test configurations"""
    
    @staticmethod
    def validate_test_suite(data: Dict[str, Any]) -> List[str]:
        """Validate test suite configuration"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'tests']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate tests array
        if 'tests' in data:
            if not isinstance(data['tests'], list):
                errors.append("'tests' must be a list")
            else:
                for i, test in enumerate(data['tests']):
                    test_errors = YAMLSchemaValidator.validate_test_case(test)
                    for error in test_errors:
                        errors.append(f"Test {i+1}: {error}")
        
        # Validate optional fields
        if 'parallel' in data and not isinstance(data['parallel'], bool):
            errors.append("'parallel' must be a boolean")
        
        if 'max_workers' in data and not isinstance(data['max_workers'], int):
            errors.append("'max_workers' must be an integer")
        
        if 'fail_fast' in data and not isinstance(data['fail_fast'], bool):
            errors.append("'fail_fast' must be a boolean")
        
        return errors
    
    @staticmethod
    def validate_test_case(data: Dict[str, Any]) -> List[str]:
        """Validate individual test case"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'prompt']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate field types
        if 'timeout' in data and not isinstance(data['timeout'], (int, float)):
            errors.append("'timeout' must be a number")
        
        if 'retry_count' in data and not isinstance(data['retry_count'], int):
            errors.append("'retry_count' must be an integer")
        
        if 'tags' in data and not isinstance(data['tags'], list):
            errors.append("'tags' must be a list")
        
        if 'variables' in data and not isinstance(data['variables'], dict):
            errors.append("'variables' must be a dictionary")
        
        return errors
    
    @staticmethod
    def validate_browser_config(data: Dict[str, Any]) -> List[str]:
        """Validate browser configuration"""
        errors = []
        
        if 'type' in data:
            valid_types = [bt.value for bt in BrowserType]
            if data['type'] not in valid_types:
                errors.append(f"Invalid browser type. Must be one of: {valid_types}")
        
        if 'headless' in data and not isinstance(data['headless'], bool):
            errors.append("'headless' must be a boolean")
        
        if 'viewport' in data:
            if not isinstance(data['viewport'], dict):
                errors.append("'viewport' must be a dictionary")
            else:
                required_viewport_keys = ['width', 'height']
                for key in required_viewport_keys:
                    if key not in data['viewport']:
                        errors.append(f"Missing viewport field: {key}")
                    elif not isinstance(data['viewport'][key], int):
                        errors.append(f"Viewport {key} must be an integer")
        
        return errors
    
    @staticmethod
    def get_schema_template() -> Dict[str, Any]:
        """Get a template for creating new test suites"""
        return {
            "name": "Example Test Suite",
            "description": "A sample test suite for browser automation",
            "base_url": "https://example.com",
            "parallel": False,
            "max_workers": 2,
            "fail_fast": False,

            "default_browser": {
                "type": "chrome",
                "headless": False,
                "viewport": {"width": 1920, "height": 1080},
                "timeout": 30000
            },
            "variables": {
                "test_user": "demo@example.com",
                "test_password": "password123"
            },
            "setup_prompt": "Navigate to the homepage and ensure the page loads correctly",
            "teardown_prompt": "Clear any session data and close any open dialogs",
            "tests": [
                {
                    "name": "Homepage Navigation",
                    "prompt": "Navigate to the homepage and verify it loads correctly with all main elements visible",
                    "success_criteria": "Page title is correct, navigation menu is visible, and main content loads",
                    "timeout": 30,
                    "tags": ["smoke", "navigation"]
                },
                {
                    "name": "User Login Flow",
                    "prompt": "Navigate to login page, enter credentials, and verify successful login",
                    "success_criteria": "User is redirected to dashboard and username is displayed",
                    "timeout": 45,
                    "tags": ["authentication", "critical"]
                }
            ],
            "report_format": ["html", "json"],
            "output_dir": "reports"
        }