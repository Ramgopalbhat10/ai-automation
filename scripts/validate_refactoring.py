#!/usr/bin/env python3
"""
Validation script to verify the refactored BrowserTest AI system.

This script validates:
1. YAML configuration system
2. Simplified schema validation
3. Example test suite loading
4. Project structure integrity
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent  # Go up one level from scripts to project root
sys.path.insert(0, str(project_root))

def validate_project_structure():
    """Validate that the refactored project structure is correct."""
    print("🔍 Validating project structure...")
    
    required_dirs = [
        "config",
        "llm_integration", 
        "test_engine",
        "test_suites",
        "test_suites/examples",
        "test_suites/production",
        "test_suites/staging",
        "reports"
    ]
    
    required_files = [
        "config/yaml_schema.py",
        "config/yaml_loader.py",
        "config/test_config.py",
        "test_suites/examples/example_test_suite.yaml",
        "README.md",
        "setup.py",
        "requirements.txt",
        "tasks.md"
    ]
    
    # Check directories
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"  ✅ Directory: {dir_path}")
        else:
            print(f"  ❌ Missing directory: {dir_path}")
            return False
    
    # Check files
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists() and full_path.is_file():
            print(f"  ✅ File: {file_path}")
        else:
            print(f"  ❌ Missing file: {file_path}")
            return False
    
    # Check that old browsertest_ai directory is gone
    old_dir = project_root / "browsertest_ai"
    if not old_dir.exists():
        print(f"  ✅ Old browsertest_ai directory removed")
    else:
        print(f"  ❌ Old browsertest_ai directory still exists")
        return False
    
    return True

def validate_yaml_system():
    """Validate the YAML configuration system."""
    print("\n🔍 Validating YAML configuration system...")
    
    try:
        # Add config directory to path for imports
        config_path = project_root / "config"
        sys.path.insert(0, str(config_path))
        
        # Import the configuration modules
        from yaml_schema import YAMLSchemaValidator, TestSuite, TestCase, BrowserConfig
        from yaml_loader import YAMLLoader
        
        print("  ✅ Successfully imported configuration modules")
        
        # Test schema validation
        validator = YAMLSchemaValidator()
        
        # Test valid configuration
        valid_config = {
            "name": "Test Suite",
            "description": "A test suite",
            "base_url": "https://example.com",
            "default_browser": {
                "type": "chrome",
                "headless": False,
                "viewport": {"width": 1920, "height": 1080}
            },
            "tests": [{
                "name": "Test Case",
                "prompt": "Navigate to homepage and verify it loads",
                "success_criteria": "Page loads successfully"
            }]
        }
        
        errors = validator.validate_test_suite(valid_config)
        if not errors:
            print("  ✅ Schema validation works correctly")
        else:
            print(f"  ❌ Schema validation failed: {errors}")
            return False
        
        # Test YAML loader
        loader = YAMLLoader()
        
        # Test template generation
        template = YAMLSchemaValidator.get_schema_template()
        if template and "name" in template:
            print("  ✅ Template generation works")
        else:
            print("  ❌ Template generation failed")
            return False
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

def validate_example_test_suite():
    """Validate the example test suite."""
    print("\n🔍 Validating example test suite...")
    
    try:
        # Add config directory to path for imports
        config_path = project_root / "config"
        sys.path.insert(0, str(config_path))
        
        from yaml_loader import YAMLLoader
        
        loader = YAMLLoader()
        example_path = project_root / "test_suites" / "examples" / "example_test_suite.yaml"
        
        if not example_path.exists():
            print(f"  ❌ Example test suite not found: {example_path}")
            return False
        
        # Load and validate the example
        test_suite = loader.load_test_suite(str(example_path))
        
        if test_suite and test_suite.name:
            print(f"  ✅ Successfully loaded: {test_suite.name}")
            print(f"  ✅ Test cases: {len(test_suite.tests)}")
            
            # Validate test case structure
            for i, test_case in enumerate(test_suite.tests):
                if hasattr(test_case, 'prompt') and test_case.prompt:
                    print(f"    ✅ Test {i+1}: Has prompt")
                else:
                    print(f"    ❌ Test {i+1}: Missing prompt")
                    return False
            
            return True
        else:
            print("  ❌ Failed to load test suite")
            return False
            
    except Exception as e:
        print(f"  ❌ Error loading example: {e}")
        return False

def validate_simplified_approach():
    """Validate that the simplified approach is working."""
    print("\n🔍 Validating simplified prompt-based approach...")
    
    try:
        # Add config directory to path for imports
        config_path = project_root / "config"
        sys.path.insert(0, str(config_path))
        
        from yaml_schema import TestCase, BrowserConfig
        
        # Test creating a simple test case with just a prompt
        test_case = TestCase(
            name="Simple Test",
            prompt="Navigate to homepage and check if it loads correctly",
            success_criteria="Page loads without errors"
        )
        
        if test_case.prompt and "navigate" in test_case.prompt.lower():
            print("  ✅ Natural language prompt approach works")
        else:
            print("  ❌ Prompt-based approach failed")
            return False
        
        # Test browser config simplicity
        from yaml_schema import BrowserType
        
        browser_config = BrowserConfig(
            type=BrowserType.CHROME,
            headless=False,
            viewport={"width": 1920, "height": 1080}
        )
        
        if browser_config.type == BrowserType.CHROME:
            print("  ✅ Simplified browser configuration works")
        else:
            print("  ❌ Browser configuration failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error in simplified approach: {e}")
        return False

def main():
    """Main validation function."""
    print("BrowserTest AI - Refactoring Validation")
    print("=" * 50)
    
    validations = [
        validate_project_structure,
        validate_yaml_system,
        validate_example_test_suite,
        validate_simplified_approach
    ]
    
    results = []
    for validation in validations:
        try:
            result = validation()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Validation failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    
    if all(results):
        print("🎉 All validations passed! Refactoring successful.")
        print("\n✨ Key improvements:")
        print("  • Flattened project structure (no nested browsertest_ai/)")
        print("  • Organized test suites in dedicated test_suites/ directory")
        print("  • Simplified YAML schema for natural language prompts")
        print("  • Removed complex action/assertion definitions")
        print("  • Maintained backward compatibility where possible")
        print("\n🚀 Ready for next development phase!")
        return True
    else:
        print("❌ Some validations failed. Please check the issues above.")
        failed_count = len([r for r in results if not r])
        print(f"   {failed_count}/{len(results)} validations failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)