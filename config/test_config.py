#!/usr/bin/env python3
"""Test script for simplified YAML configuration system"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from yaml_schema import (
    TestSuite, TestCase, BrowserConfig, YAMLSchemaValidator,
    BrowserType, Environment
)
from yaml_loader import YAMLLoader


def test_schema_validation():
    """Test YAML schema validation"""
    print("Testing YAML schema validation...")
    
    # Test valid configuration
    valid_config = {
        "name": "Test Suite",
        "description": "A test suite",
        "tests": [
            {
                "name": "Test Case 1",
                "prompt": "Navigate to homepage and verify it loads",
                "success_criteria": "Page loads successfully"
            }
        ]
    }
    
    errors = YAMLSchemaValidator.validate_test_suite(valid_config)
    if errors:
        print(f"❌ Valid config failed validation: {errors}")
        return False
    else:
        print("✅ Valid configuration passed validation")
    
    # Test invalid configuration
    invalid_config = {
        "name": "Test Suite",
        # Missing required 'tests' field
    }
    
    errors = YAMLSchemaValidator.validate_test_suite(invalid_config)
    if not errors:
        print("❌ Invalid config should have failed validation")
        return False
    else:
        print("✅ Invalid configuration correctly failed validation")
    
    return True


def test_data_class_creation():
    """Test creating data classes from configuration"""
    print("\nTesting data class creation...")
    
    try:
        # Test BrowserConfig creation
        browser = BrowserConfig(
            type=BrowserType.CHROME,
            headless=False,
            viewport={"width": 1920, "height": 1080}
        )
        print(f"✅ BrowserConfig created: {browser.type.value}, headless={browser.headless}")
        
        # Test TestCase creation
        test_case = TestCase(
            name="Sample Test",
            prompt="Test the homepage functionality",
            success_criteria="Homepage loads and displays correctly",
            browser=browser
        )
        print(f"✅ TestCase created: {test_case.name}")
        
        # Test TestSuite creation
        test_suite = TestSuite(
            name="Sample Suite",
            description="A sample test suite",
            tests=[test_case]
        )
        print(f"✅ TestSuite created: {test_suite.name} with {len(test_suite.tests)} test(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Data class creation failed: {e}")
        return False


def test_yaml_loader():
    """Test YAML loader functionality"""
    print("\nTesting YAML loader...")
    
    try:
        # Test template generation
        template = YAMLSchemaValidator.get_schema_template()
        print(f"✅ Schema template generated with {len(template['tests'])} test(s)")
        
        # Test creating a temporary YAML file
        temp_file = Path(__file__).parent / "temp_test.yaml"
        YAMLLoader.create_template(str(temp_file))
        print(f"✅ Template YAML file created: {temp_file}")
        
        # Test loading the YAML file
        test_suite = YAMLLoader.load_test_suite(str(temp_file))
        print(f"✅ YAML file loaded: {test_suite.name} with {len(test_suite.tests)} test(s)")
        
        # Clean up
        temp_file.unlink()
        print("✅ Temporary file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ YAML loader test failed: {e}")
        return False


def test_example_yaml():
    """Test loading the example YAML file"""
    print("\nTesting example YAML file...")
    
    try:
        # Path to example YAML file
        example_file = Path(__file__).parent.parent / "test_suites" / "examples" / "example_test_suite.yaml"
        
        if not example_file.exists():
            print(f"❌ Example file not found: {example_file}")
            return False
        
        # Validate schema
        errors = YAMLLoader.validate_schema(str(example_file))
        if errors:
            print(f"❌ Example YAML validation failed: {errors}")
            return False
        
        # Load the file
        test_suite = YAMLLoader.load_test_suite(str(example_file))
        print(f"✅ Example YAML loaded: {test_suite.name}")
        print(f"   - Tests: {len(test_suite.tests)}")
        print(f"   - Environment: {test_suite.default_environment.value}")
        print(f"   - Browser: {test_suite.default_browser.type.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Example YAML test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Testing Simplified YAML Configuration System\n")
    
    tests = [
        test_schema_validation,
        test_data_class_creation,
        test_yaml_loader,
        test_example_yaml
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("\n⚠️  Test failed, continuing with remaining tests...")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The simplified YAML configuration system is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())