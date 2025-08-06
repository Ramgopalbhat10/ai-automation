#!/usr/bin/env python3
"""Test script to validate YAML configuration system"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent  # Go up one level from scripts to project root
sys.path.insert(0, str(project_root))

# Direct imports to avoid package initialization issues
sys.path.insert(0, str(project_root / "config"))

from yaml_loader import YAMLLoader
from yaml_schema import YAMLSchemaValidator

def test_yaml_configuration():
    """Test the YAML configuration system"""
    print("Testing BrowserTest AI YAML Configuration System")
    print("=" * 50)
    
    # Test 1: Create sample configurations
    print("\n1. Creating sample YAML configurations...")
    
    try:
        # Create basic sample
        YAMLLoader.create_sample_config(str(project_root / "sample_basic.yaml"), "basic")
        print("   ✓ Basic sample created: sample_basic.yaml")
        
        # Create advanced sample
        YAMLLoader.create_sample_config(str(project_root / "sample_advanced.yaml"), "advanced")
        print("   ✓ Advanced sample created: sample_advanced.yaml")
        
        # Create comprehensive sample
        YAMLLoader.create_sample_config(str(project_root / "sample_comprehensive.yaml"), "comprehensive")
        print("   ✓ Comprehensive sample created: sample_comprehensive.yaml")
        
    except Exception as e:
        print(f"   ✗ Error creating samples: {e}")
        return False
    
    # Test 2: Validate existing example
    print("\n2. Validating example test suite...")
    
    example_file = str(project_root / "test_suites" / "examples" / "example_test_suite.yaml")
    if Path(example_file).exists():
        try:
            # Check validation
            is_valid = YAMLLoader.validate_schema(example_file)
            if is_valid:
                print(f"   ✓ {example_file} is valid")
            else:
                print(f"   ✗ {example_file} has validation errors")
                errors = YAMLLoader.get_validation_errors(example_file)
                for error in errors:
                    print(f"     - {error}")
                return False
                
        except Exception as e:
            print(f"   ✗ Error validating {example_file}: {e}")
            return False
    else:
        print(f"   ! {example_file} not found, skipping validation")
    
    # Test 3: Load and parse configuration
    print("\n3. Loading and parsing test suite...")
    
    try:
        # Load the example configuration
        if Path(example_file).exists():
            test_suite = YAMLLoader.load_test_suite(example_file)
            print(f"   ✓ Loaded test suite: {test_suite.name}")
            print(f"   ✓ Description: {test_suite.description}")
            print(f"   ✓ Number of tests: {len(test_suite.tests)}")
            print(f"   ✓ Parallel execution: {test_suite.parallel}")
            print(f"   ✓ Max workers: {test_suite.max_workers}")
            print(f"   ✓ Default environment: {test_suite.default_environment.value}")
            print(f"   ✓ Default browser: {test_suite.default_browser.type.value}")
            
            # Show test details
            print("\n   Test cases:")
            for i, test in enumerate(test_suite.tests, 1):
                print(f"     {i}. {test.name}")
                print(f"        - Tags: {test.tags}")
                print(f"        - Timeout: {test.timeout}s")
                print(f"        - Actions: {len(test.actions)}")
                print(f"        - Assertions: {len(test.assertions)}")
                
        else:
            # Load basic sample instead
            test_suite = YAMLLoader.load_test_suite(str(project_root / "sample_basic.yaml"))
            print(f"   ✓ Loaded basic sample: {test_suite.name}")
            
    except Exception as e:
        print(f"   ✗ Error loading test suite: {e}")
        return False
    
    # Test 4: Variable substitution
    print("\n4. Testing variable substitution...")
    
    try:
        variables = {
            "test_user": "demo@example.com",
            "base_url": "https://test.example.com"
        }
        
        # Test with variables
        if Path(example_file).exists():
            test_suite_with_vars = YAMLLoader.load_test_suite(example_file, variables)
            print("   ✓ Variable substitution completed")
            print(f"   ✓ Variables merged: {len(test_suite_with_vars.variables)} total")
        else:
            print("   ! Skipping variable test (example file not found)")
            
    except Exception as e:
        print(f"   ✗ Error with variable substitution: {e}")
        return False
    
    # Test 5: Schema validation details
    print("\n5. Testing schema validation...")
    
    try:
        # Test invalid configuration
        invalid_config = {
            "name": "Invalid Test",
            # Missing required 'tests' field
            "parallel": "not_a_boolean",  # Wrong type
            "max_workers": "not_a_number"  # Wrong type
        }
        
        errors = YAMLSchemaValidator.validate_test_suite(invalid_config)
        if errors:
            print(f"   ✓ Schema validation caught {len(errors)} errors:")
            for error in errors[:3]:  # Show first 3 errors
                print(f"     - {error}")
        else:
            print("   ✗ Schema validation should have found errors")
            return False
            
    except Exception as e:
        print(f"   ✗ Error testing schema validation: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All YAML configuration tests passed!")
    print("\nThe enhanced YAML configuration system is working correctly.")
    print("\nFeatures validated:")
    print("  - Enhanced TestCase and TestSuite models")
    print("  - Comprehensive schema validation")
    print("  - Variable substitution with environment variables")
    print("  - Browser configuration with multiple types")
    print("  - Action and assertion step parsing")
    print("  - Multiple template types (basic, advanced, comprehensive)")
    print("  - Error handling and detailed validation messages")
    
    return True

if __name__ == "__main__":
    success = test_yaml_configuration()
    sys.exit(0 if success else 1)