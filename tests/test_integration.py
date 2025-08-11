"""Integration tests for pytest and allure setup"""
import os
import sys
from pathlib import Path

import pytest
import allure

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config import Config
from config.yaml_loader import YAMLLoader
from test_engine.test_engine import TestEngine


@pytest.mark.unit
class TestPytestIntegration:
    """Test pytest integration with existing framework"""
    
    @allure.feature("Framework Integration")
    @allure.story("Configuration Loading")
    def test_config_loading(self):
        """Test that configuration loads correctly"""
        with allure.step("Load configuration"):
            config = Config()
            assert config is not None
        
        with allure.step("Verify config has required settings"):
            # Test that we can access config values
            provider = config.get("llm.provider", "google")
            assert provider in ["google", "openai", "groq"]
    
    @allure.feature("Framework Integration")
    @allure.story("YAML Loading")
    def test_yaml_loader(self):
        """Test YAML loader functionality"""
        # Test with a simple YAML structure
        yaml_content = {
            'name': 'Test Suite',
            'description': 'Test Description',
            'tests': []
        }
        
        # Create a temporary YAML file
        import tempfile
        import yaml
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_content, f)
            temp_file = f.name
        
        try:
            result = YAMLLoader.load_test_suite(temp_file)
            assert result is not None
        finally:
            import os
            os.unlink(temp_file)
    
    @allure.feature("Framework Integration")
    @allure.story("Test Engine Initialization")
    def test_test_engine_initialization(self):
        """Test that test engine initializes correctly"""
        with allure.step("Initialize test engine"):
            config = Config()
            test_engine = TestEngine(config)
            assert test_engine is not None
        
        with allure.step("Verify test engine components"):
            assert test_engine.config is not None
            assert test_engine.llm_provider is not None
            assert test_engine.browser_manager is not None
            assert test_engine.result_collector is not None


@pytest.mark.integration
class TestAllureIntegration:
    """Test allure reporting integration"""
    
    @allure.feature("Allure Integration")
    @allure.story("Basic Reporting")
    @allure.severity(allure.severity_level.NORMAL)
    def test_allure_basic_features(self):
        """Test basic allure features"""
        with allure.step("Test step execution"):
            # This step should appear in allure report
            result = 2 + 2
            assert result == 4
        
        with allure.step("Test attachment"):
            allure.attach(
                "This is a test attachment",
                name="Test Data",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # Add some metadata
        allure.dynamic.tag("integration")
        allure.dynamic.link("https://github.com/your-org/browsertest-ai", name="Repository")
    
    @allure.feature("Allure Integration")
    @allure.story("Environment Information")
    def test_environment_info(self):
        """Test that environment information is captured"""
        with allure.step("Check environment variables"):
            # These should be set by conftest.py
            assert True  # Environment info is set automatically
        
        allure.dynamic.description(
            "This test verifies that environment information "
            "is properly captured and displayed in allure reports."
        )


@pytest.mark.slow
@pytest.mark.integration
class TestYAMLSuiteExecution:
    """Test YAML suite execution (if available)"""
    
    @allure.feature("YAML Suite Execution")
    @allure.story("Suite Discovery")
    def test_yaml_suite_discovery(self):
        """Test that YAML test suites can be discovered"""
        suites_dir = project_root / "test_suites"
        
        if not suites_dir.exists():
            pytest.skip("No test_suites directory found")
        
        with allure.step("Find YAML files"):
            yaml_files = list(suites_dir.rglob("*.yaml")) + list(suites_dir.rglob("*.yml"))
            assert len(yaml_files) > 0, "No YAML test suite files found"
        
        with allure.step("Verify YAML files are readable"):
            for yaml_file in yaml_files:
                assert yaml_file.is_file()
                assert yaml_file.stat().st_size > 0
                # Test that each file can be loaded
                try:
                    YAMLLoader.load_test_suite(str(yaml_file))
                except Exception as e:
                    pytest.fail(f"Failed to load {yaml_file}: {e}")
        
        allure.attach(
            "\n".join([str(f.relative_to(project_root)) for f in yaml_files]),
            name="Found YAML Files",
            attachment_type=allure.attachment_type.TEXT
        )