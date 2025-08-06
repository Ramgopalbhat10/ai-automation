#!/usr/bin/env python3
"""Simplified YAML loader for prompt-based test configurations"""

import yaml
from typing import Dict, Any, List
from pathlib import Path
from .yaml_schema import (
    TestSuite, TestCase, BrowserConfig,
    YAMLSchemaValidator, BrowserType
)


class YAMLLoader:
    """Loads and validates YAML test configurations"""
    
    @staticmethod
    def load_test_suite(file_path: str) -> TestSuite:
        """Load test suite from YAML file
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            TestSuite object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML is invalid
            ValueError: If validation fails
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Test suite file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        # Validate schema
        errors = YAMLSchemaValidator.validate_test_suite(data)
        if errors:
            raise ValueError(f"YAML validation failed:\n" + "\n".join(errors))
        
        return YAMLLoader._create_test_suite(data)
    
    @staticmethod
    def validate_schema(file_path: str) -> List[str]:
        """Validate YAML file against schema without loading
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            List of validation errors (empty if valid)
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return [f"File not found: {file_path}"]
            
            with open(path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            
            return YAMLSchemaValidator.validate_test_suite(data)
        
        except yaml.YAMLError as e:
            return [f"YAML parsing error: {str(e)}"]
        except Exception as e:
            return [f"Error reading file: {str(e)}"]
    
    @staticmethod
    def save_test_suite(test_suite: TestSuite, file_path: str) -> None:
        """Save test suite to YAML file
        
        Args:
            test_suite: TestSuite object to save
            file_path: Output file path
        """
        data = YAMLLoader._test_suite_to_dict(test_suite)
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, default_flow_style=False, indent=2, sort_keys=False)
    
    @staticmethod
    def create_template(file_path: str) -> None:
        """Create a template YAML file
        
        Args:
            file_path: Output file path for template
        """
        template = YAMLSchemaValidator.get_schema_template()
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as file:
            yaml.dump(template, file, default_flow_style=False, indent=2, sort_keys=False)
    
    @staticmethod
    def _create_test_suite(data: Dict[str, Any]) -> TestSuite:
        """Create TestSuite object from validated data"""
        # Extract tests
        tests = []
        for test_data in data.get('tests', []):
            test_case = YAMLLoader._create_test_case(test_data, data)
            tests.append(test_case)
        
        # Create default browser config
        default_browser_data = data.get('default_browser', {})
        default_browser = YAMLLoader._create_browser_config(default_browser_data)
        
        # Create test suite
        test_suite = TestSuite(
            name=data['name'],
            description=data.get('description', ''),
            tests=tests,
            parallel=data.get('parallel', False),
            max_workers=data.get('max_workers', 2),
            fail_fast=data.get('fail_fast', False),

            default_browser=default_browser,
            default_llm_provider=data.get('default_llm_provider', 'google'),
            default_llm_model=data.get('default_llm_model'),
            base_url=data.get('base_url', ''),
            setup_prompt=data.get('setup_prompt', ''),
            teardown_prompt=data.get('teardown_prompt', ''),
            variables=data.get('variables', {}),
            data_sources=data.get('data_sources', {}),
            report_format=data.get('report_format', ['html', 'json']),
            output_dir=data.get('output_dir', 'reports')
        )
        
        return test_suite
    
    @staticmethod
    def _create_test_case(test_data: Dict[str, Any], suite_data: Dict[str, Any]) -> TestCase:
        """Create TestCase object from test data"""
        # Inherit defaults from suite
        default_browser_data = suite_data.get('default_browser', {})
        test_browser_data = test_data.get('browser', default_browser_data)
        browser = YAMLLoader._create_browser_config(test_browser_data)
        
        # Merge variables
        suite_variables = suite_data.get('variables', {})
        test_variables = test_data.get('variables', {})
        merged_variables = {**suite_variables, **test_variables}
        
        # Create test case
        test_case = TestCase(
            name=test_data['name'],
            prompt=test_data['prompt'],
            success_criteria=test_data.get('success_criteria', ''),
            description=test_data.get('description', ''),
            url=test_data.get('url', ''),
            timeout=test_data.get('timeout', 120),
            retry_count=test_data.get('retry_count', 1),
            tags=test_data.get('tags', []),
            environment=test_data.get('environment', 'production'),

            browser=browser,
            llm_provider=test_data.get('llm_provider', suite_data.get('default_llm_provider', 'google')),
            llm_model=test_data.get('llm_model', suite_data.get('default_llm_model')),
            llm_temperature=test_data.get('llm_temperature', 0.1),
            max_actions=test_data.get('max_actions', 50),
            variables=merged_variables,
            data_file=test_data.get('data_file'),
            setup_prompt=test_data.get('setup_prompt', ''),
            teardown_prompt=test_data.get('teardown_prompt', '')
        )
        
        return test_case
    
    @staticmethod
    def _create_browser_config(browser_data: Dict[str, Any]) -> BrowserConfig:
        """Create BrowserConfig object from browser data"""
        if not browser_data:
            return BrowserConfig()
        
        return BrowserConfig(
            type=BrowserType(browser_data.get('type', 'chromium')),
            headless=browser_data.get('headless', True),
            viewport=browser_data.get('viewport', {'width': 1920, 'height': 1080}),
            timeout=browser_data.get('timeout', 30000),
            slow_mo=browser_data.get('slow_mo', 0),
            args=browser_data.get('args', [])
        )
    
    @staticmethod
    def _test_suite_to_dict(test_suite: TestSuite) -> Dict[str, Any]:
        """Convert TestSuite object to dictionary for YAML export"""
        return {
            'name': test_suite.name,
            'description': test_suite.description,
            'base_url': test_suite.base_url,
            'parallel': test_suite.parallel,
            'max_workers': test_suite.max_workers,
            'fail_fast': test_suite.fail_fast,

            'default_browser': {
                'type': test_suite.default_browser.type.value,
                'headless': test_suite.default_browser.headless,
                'viewport': test_suite.default_browser.viewport,
                'timeout': test_suite.default_browser.timeout,
                'slow_mo': test_suite.default_browser.slow_mo,
                'args': test_suite.default_browser.args
            },
            'setup_prompt': test_suite.setup_prompt,
            'teardown_prompt': test_suite.teardown_prompt,
            'variables': test_suite.variables,
            'data_sources': test_suite.data_sources,
            'tests': [
                {
                    'name': test.name,
                    'prompt': test.prompt,
                    'success_criteria': test.success_criteria,
                    'description': test.description,
                    'url': test.url,
                    'timeout': test.timeout,
                    'retry_count': test.retry_count,
                    'tags': test.tags,

                    'browser': {
                        'type': test.browser.type.value,
                        'headless': test.browser.headless,
                        'viewport': test.browser.viewport,
                        'timeout': test.browser.timeout,
                        'slow_mo': test.browser.slow_mo,
                        'args': test.browser.args
                    },
                    'llm_model': test.llm_model,
                    'llm_temperature': test.llm_temperature,
                    'max_actions': test.max_actions,
                    'variables': test.variables,
                    'data_file': test.data_file,
                    'setup_prompt': test.setup_prompt,
                    'teardown_prompt': test.teardown_prompt
                }
                for test in test_suite.tests
            ],
            'report_format': test_suite.report_format,
            'output_dir': test_suite.output_dir
        }