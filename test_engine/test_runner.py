"""Individual test runner with browser-use integration"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from browser_use import Agent

from config import Config
from config.yaml_loader import TestCase
from config.environment import EnvironmentManager
from llm_integration.llm_provider import LLMProvider
from llm_integration.browser_use_integration import BrowserUseIntegration
from browser_manager import BrowserManager
from .result_collector import TestResult


class TestRunner:
    """Runs individual test cases using browser-use"""
    
    def __init__(
        self,
        config: Config,
        llm_provider: LLMProvider,
        browser_manager: BrowserManager,
        environment_manager: EnvironmentManager
    ):
        """Initialize test runner
        
        Args:
            config: Application configuration
            llm_provider: LLM provider instance
            browser_manager: Browser manager instance
            environment_manager: Environment manager instance
        """
        self.config = config
        self.llm_provider = llm_provider
        self.browser_manager = browser_manager
        self.environment_manager = environment_manager
        self.browser_use_integration = BrowserUseIntegration(config, llm_provider)
    
    async def run_test(self, test_case: TestCase) -> TestResult:
        """Run a single test case
        
        Args:
            test_case: Test case configuration
            
        Returns:
            Test execution result
        """
        start_time = datetime.now()
        
        try:
            # Set environment for this test
            if test_case.environment:
                # Convert Environment enum to string value
                env_name = test_case.environment.value if hasattr(test_case.environment, 'value') else str(test_case.environment)
                self.environment_manager.set_current_environment(env_name)
            
            # Create LLM provider for this test case if specified
            test_llm_provider = self._get_test_llm_provider(test_case)
            
            # Resolve URL if provided
            url = self._resolve_test_url(test_case.url)
            
            # Create comprehensive task for the agent
            full_task = self._create_full_task(test_case, url)
            
            # Execute test with retries using BrowserUseIntegration
            result = await self._execute_with_retries(
                test_case,
                full_task,
                test_llm_provider
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                test_name=test_case.name,
                status="passed" if result.get("success", False) else "failed",
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                output=result.get("output", ""),
                error_message=result.get("error"),
                screenshots=result.get("screenshots", []),
                metadata={
                    "url": url,
                    "browser": test_case.browser,
                    "environment": test_case.environment,
                    "tags": test_case.tags,
                    "retry_count": result.get("retry_count", 0)
                }
            )
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                test_name=test_case.name,
                status="error",
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                error_message=str(e),
                metadata={
                    "url": test_case.url,
                    "browser": test_case.browser,
                    "environment": test_case.environment,
                    "tags": test_case.tags
                }
            )
    
    def _create_full_task(self, test_case: TestCase, url: str) -> str:
        """Create comprehensive task description for the Agent
        
        Args:
            test_case: Test case configuration
            url: Resolved URL
            
        Returns:
            Full task description
        """
        task_parts = []
        
        # Add URL navigation
        if url:
            task_parts.append(f"1. Navigate to {url}")
        
        # Add main task
        task_parts.append(f"2. {test_case.prompt}")
        
        # Add expected outcome validation if specified
        if hasattr(test_case, 'expected_outcome') and test_case.expected_outcome:
            task_parts.append(f"3. Verify that: {test_case.expected_outcome}")
        
        return "\n".join(task_parts)
    
    async def _execute_with_retries(
        self,
        test_case: TestCase,
        full_task: str,
        llm_provider: Optional[LLMProvider] = None
    ) -> Dict[str, Any]:
        """Execute test with retry logic using Context7Integration
        
        Args:
            test_case: Test case configuration
            full_task: Complete task description
            llm_provider: Optional LLM provider for this test
            
        Returns:
            Execution result
        """
        last_error = None
        
        for attempt in range(test_case.retry_count + 1):
            try:
                if attempt > 0:
                    print(f"Retrying test {test_case.name} (attempt {attempt + 1})")
                    await asyncio.sleep(self.config.get("execution.retry_delay", 5))
                
                # Configure agent settings
                agent_config = {
                    "use_vision": self.config.get("agent.use_vision", True),
                    "max_steps": test_case.timeout or self.config.get("agent.max_steps", 50),
                    "save_conversation_path": self.config.get("agent.save_conversation_path")
                }
                
                # Add sensitive data if configured for this environment
                if test_case.environment:
                    sensitive_data = self._get_sensitive_data(test_case.environment)
                    if sensitive_data:
                        agent_config["sensitive_data"] = sensitive_data
                
                # Use test-specific LLM provider if available
                integration_to_use = self.browser_use_integration
                if llm_provider:
                    # Create a temporary integration with the test-specific provider
                    from llm_integration.browser_use_integration import BrowserUseIntegration
                    integration_to_use = BrowserUseIntegration(
                        config=self.config,
                        llm_provider=llm_provider
                    )
                
                # Execute the test task using BrowserUseIntegration
                result = await asyncio.wait_for(
                    integration_to_use.run_agent(
                        task=full_task,
                        **agent_config
                    ),
                    timeout=test_case.timeout
                )
                
                # Capture screenshots if enabled
                screenshots = []
                if self.config.get("reporting.screenshots", True):
                    screenshot = await self._capture_screenshot_from_agent()
                    if screenshot:
                        screenshots.append(screenshot)
                
                return {
                    "success": True,
                    "output": str(result),
                    "screenshots": screenshots,
                    "retry_count": attempt
                }
                
            except asyncio.TimeoutError:
                last_error = f"Test timed out after {test_case.timeout} seconds"
                print(f"Test {test_case.name} timed out on attempt {attempt + 1}")
                
            except Exception as e:
                last_error = str(e)
                print(f"Test {test_case.name} failed on attempt {attempt + 1}: {e}")
        
        return {
            "success": False,
            "error": last_error,
            "retry_count": test_case.retry_count
        }
    
    def _resolve_test_url(self, url: str) -> str:
        """Resolve test URL using environment manager
        
        Args:
            url: URL path or full URL
            
        Returns:
            Resolved full URL
        """
        if not url:
            return ""
        
        # If it's already a full URL, return as-is
        if url.startswith(('http://', 'https://')):
            return url
        
        # Resolve using environment manager
        try:
            return self.environment_manager.resolve_url(url)
        except ValueError:
            # Fallback to base URL from config
            base_url = self.config.get("environment.base_url", "")
            if base_url:
                return f"{base_url.rstrip('/')}/{url.lstrip('/')}"
            return url
    
    def _get_sensitive_data(self, environment: str) -> Optional[Dict[str, Dict[str, str]]]:
        """Get sensitive data configuration for environment
        
        Args:
            environment: Environment name
            
        Returns:
            Sensitive data configuration or None
        """
        env = self.environment_manager.get_environment(environment)
        return env.credentials if env else None
    
    async def _capture_screenshot_from_agent(self) -> Optional[str]:
        """Capture screenshot using current agent
        
        Returns:
            Screenshot file path or None
        """
        try:
            if self.browser_use_integration.current_agent:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"screenshots/test_{timestamp}.png"
                
                # Create screenshots directory if it doesn't exist
                import os
                os.makedirs("screenshots", exist_ok=True)
                
                # Note: Screenshot capture would need to be implemented
                # based on the current browser-use API
                return screenshot_path
            return None
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
            return None
    
    async def _capture_screenshot(self, browser) -> Optional[str]:
        """Capture screenshot of current page
        
        Args:
            browser: Browser instance
            
        Returns:
            Screenshot file path or None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/test_{timestamp}.png"
            
            # Create screenshots directory if it doesn't exist
            import os
            os.makedirs("screenshots", exist_ok=True)
            
            # Capture screenshot
            await browser.screenshot(path=screenshot_path)
            return screenshot_path
            
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
            return None
    
    def _get_test_llm_provider(self, test_case: TestCase) -> Optional[LLMProvider]:
        """Get LLM provider for the test case
        
        Args:
            test_case: Test case configuration
            
        Returns:
            LLM provider instance or None to use default
        """
        from llm_integration.llm_provider import LLMProvider
        
        # Use test case specific provider if specified
        if hasattr(test_case, 'llm_provider') and test_case.llm_provider:
            provider_name = test_case.llm_provider
            
            # Get model and temperature from test case or use defaults
            model = getattr(test_case, 'llm_model', None)
            temperature = getattr(test_case, 'llm_temperature', 0.7)
            
            try:
                # Create a temporary config with the test-specific settings
                temp_config = Config()
                temp_config.llm_provider = provider_name
                if model:
                    temp_config.llm_model = model
                if temperature is not None:
                    temp_config.llm_temperature = temperature
                    
                return LLMProvider.create_provider(provider_name, temp_config)
            except Exception as e:
                print(f"Failed to create LLM provider '{provider_name}': {e}")
                print("Falling back to default provider")
                return None
        
        return None
    
    async def cleanup(self):
        """Cleanup test runner resources"""
        await self.browser_use_integration.cleanup()