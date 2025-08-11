"""Pytest configuration and shared fixtures"""
import os
import sys
import asyncio
from pathlib import Path
from typing import Generator

import pytest
import allure
from allure_commons.types import AttachmentType

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config import Config
from browser_manager import BrowserManager
from llm_integration.llm_provider import LLMProvider


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def config() -> Config:
    """Provide application configuration for tests"""
    return Config()


@pytest.fixture(scope="session")
async def browser_manager(config: Config) -> BrowserManager:
    """Provide browser manager for tests"""
    manager = BrowserManager(config)
    yield manager
    # Cleanup browsers after session
    await manager.cleanup_all()


@pytest.fixture(scope="session")
def llm_provider(config: Config) -> LLMProvider:
    """Provide LLM provider for tests"""
    provider_type = config.get("llm.provider", "google")
    return LLMProvider.create_provider(provider_type, config)


@pytest.fixture(autouse=True)
def setup_allure_environment():
    """Setup allure environment information"""
    # Environment information is set via allure.properties file
    # and can be added programmatically in individual tests
    pass


@pytest.fixture(autouse=True)
def capture_logs(caplog):
    """Automatically capture logs for all tests"""
    caplog.set_level("INFO")
    yield
    
    # Attach logs to allure report if test fails
    if caplog.records:
        log_content = "\n".join([record.getMessage() for record in caplog.records])
        allure.attach(
            log_content,
            name="Test Logs",
            attachment_type=AttachmentType.TEXT
        )


def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Ensure allure results directory exists
    allure_dir = config.getoption("--allure-dir", default="allure-results")
    os.makedirs(allure_dir, exist_ok=True)
    
    # Add custom markers
    config.addinivalue_line(
        "markers", "yaml_suite: mark test as a YAML test suite test"
    )
    config.addinivalue_line(
        "markers", "browser: mark test as a browser automation test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--yaml-suite",
        action="store",
        default=None,
        help="Path to YAML test suite file"
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to use for testing (chrome, firefox, safari, edge)"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode"
    )


def pytest_runtest_makereport(item, call):
    """Hook to capture test results for allure"""
    if call.when == "call":
        # Add test metadata to allure
        if hasattr(item, "function"):
            allure.dynamic.description_html(
                f"<p><b>Test Function:</b> {item.function.__name__}</p>"
                f"<p><b>Test File:</b> {item.fspath}</p>"
                f"<p><b>Test Node ID:</b> {item.nodeid}</p>"
            )


@pytest.fixture
def yaml_suite_path(request):
    """Get YAML suite path from command line or default"""
    yaml_file = request.config.getoption("--yaml-suite")
    if not yaml_file:
        yaml_file = os.environ.get("YAML_SUITE")
    if not yaml_file:
        yaml_file = "test_suites/production/mrgb_blog_test_suite.yaml"
    
    # Convert to absolute path
    if not os.path.isabs(yaml_file):
        yaml_file = os.path.join(project_root, yaml_file)
    
    return yaml_file