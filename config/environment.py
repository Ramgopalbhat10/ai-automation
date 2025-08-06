"""Environment management for different deployment environments"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Environment:
    """Environment configuration"""
    name: str
    base_url: str
    credentials: Optional[Dict[str, str]] = None
    variables: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.credentials is None:
            self.credentials = {}
        if self.variables is None:
            self.variables = {}


class EnvironmentManager:
    """Manages multiple environments and their configurations"""
    
    def __init__(self):
        self._environments: Dict[str, Environment] = {}
        self._current_environment: Optional[str] = None
        self._setup_default_environments()
    
    def _setup_default_environments(self):
        """Setup default environments"""
        self.add_environment(Environment(
            name="development",
            base_url="http://localhost:3000",
            variables={"debug": True, "timeout": 30}
        ))
        
        self.add_environment(Environment(
            name="staging",
            base_url="https://staging.example.com",
            variables={"debug": False, "timeout": 60}
        ))
        
        self.add_environment(Environment(
            name="production",
            base_url="https://example.com",
            variables={"debug": False, "timeout": 120}
        ))
        
        self._current_environment = "development"
    
    def add_environment(self, environment: Environment):
        """Add a new environment
        
        Args:
            environment: Environment configuration
        """
        self._environments[environment.name] = environment
    
    def get_environment(self, name: str) -> Optional[Environment]:
        """Get environment by name
        
        Args:
            name: Environment name
            
        Returns:
            Environment configuration or None
        """
        return self._environments.get(name)
    
    def set_current_environment(self, name: str):
        """Set current active environment
        
        Args:
            name: Environment name
            
        Raises:
            ValueError: If environment doesn't exist
        """
        if name not in self._environments:
            raise ValueError(f"Environment '{name}' not found")
        self._current_environment = name
    
    def get_current_environment(self) -> Optional[Environment]:
        """Get current active environment
        
        Returns:
            Current environment configuration
        """
        if self._current_environment:
            return self._environments[self._current_environment]
        return None
    
    def list_environments(self) -> list[str]:
        """List all available environments
        
        Returns:
            List of environment names
        """
        return list(self._environments.keys())
    
    def resolve_url(self, path: str = "") -> str:
        """Resolve URL for current environment
        
        Args:
            path: URL path to append
            
        Returns:
            Complete URL for current environment
        """
        current_env = self.get_current_environment()
        if not current_env:
            raise ValueError("No current environment set")
        
        base_url = current_env.base_url.rstrip('/')
        path = path.lstrip('/')
        
        if path:
            return f"{base_url}/{path}"
        return base_url
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get environment variable
        
        Args:
            key: Variable key
            default: Default value if not found
            
        Returns:
            Variable value
        """
        current_env = self.get_current_environment()
        if current_env and current_env.variables:
            return current_env.variables.get(key, default)
        return default
    
    def get_credential(self, key: str) -> Optional[str]:
        """Get environment credential
        
        Args:
            key: Credential key
            
        Returns:
            Credential value or None
        """
        current_env = self.get_current_environment()
        if current_env and current_env.credentials:
            return current_env.credentials.get(key)
        return None