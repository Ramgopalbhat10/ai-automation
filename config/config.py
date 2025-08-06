"""Main configuration class for BrowserTest AI"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Central configuration management for BrowserTest AI"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration
        
        Args:
            config_file: Optional path to configuration file
        """
        self._config = {}
        self._load_environment()
        if config_file:
            self._load_config_file(config_file)
    
    def _load_environment(self):
        """Load environment variables"""
        # Load .env file if it exists
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)
        
        # Core settings
        self._config.update({
            "llm": {
                "provider": os.getenv("LLM_PROVIDER", "google"),
                "google_api_key": os.getenv("GOOGLE_API_KEY"),
                "openai_api_key": os.getenv("OPENAI_API_KEY"),
                "model": os.getenv("LLM_MODEL", "gemini-2.0-flash-exp"),
            },
            "browser": {
                "headless": os.getenv("BROWSER_HEADLESS", "true").lower() == "true",
                "browser_type": os.getenv("BROWSER_TYPE", "chromium"),
                "timeout": int(os.getenv("BROWSER_TIMEOUT", "30000")),
                "pool_size": int(os.getenv("BROWSER_POOL_SIZE", "3")),
            },
            "execution": {
                "parallel_workers": int(os.getenv("PARALLEL_WORKERS", "2")),
                "max_retries": int(os.getenv("MAX_RETRIES", "3")),
                "retry_delay": int(os.getenv("RETRY_DELAY", "5")),
            },
            "reporting": {
                "output_dir": os.getenv("OUTPUT_DIR", "reports"),
                "format": os.getenv("REPORT_FORMAT", "html,json"),
                "screenshots": os.getenv("SCREENSHOTS", "true").lower() == "true",
            },
            "base_url": os.getenv("BASE_URL")
        })
    
    def _load_config_file(self, config_file: str):
        """Load configuration from file
        
        Args:
            config_file: Path to configuration file
        """
        # TODO: Implement YAML/JSON config file loading
        pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'llm.provider')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'llm.provider')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values
        
        Returns:
            Complete configuration dictionary
        """
        return self._config.copy()
    
    def validate(self) -> bool:
        """Validate configuration
        
        Returns:
            True if configuration is valid
        """
        # Check required API keys
        provider = self.get("llm.provider")
        if provider == "google" and not self.get("llm.google_api_key"):
            raise ValueError("Google API key is required when using Google provider")
        elif provider == "openai" and not self.get("llm.openai_api_key"):
            raise ValueError("OpenAI API key is required when using OpenAI provider")
        
        return True