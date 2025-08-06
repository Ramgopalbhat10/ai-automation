"""Abstract LLM provider interface for BrowserTest AI"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from config.config import Config


class LLMProvider(ABC):
    """Abstract base class for LLM providers compatible with browser-use"""
    
    def __init__(self, config: Config):
        self.config = config
        self._llm = None
        
    @abstractmethod
    def get_llm(self):
        """Return the LLM instance compatible with browser-use Agent"""
        pass
        
    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate API credentials"""
        pass
        
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        pass
        
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name/identifier"""
        pass
        
    def test_connection(self) -> bool:
        """Test connection to the LLM service"""
        try:
            return self.validate_credentials()
        except Exception:
            return False
    
    def supports_vision(self) -> bool:
        """Check if the model supports vision capabilities"""
        model_name = self.get_model_name().lower()
        vision_models = ['gpt-4o', 'gpt-4-vision', 'claude-3', 'gemini-pro-vision', 'gemini-1.5', 'llava']
        return any(vision_model in model_name for vision_model in vision_models)
    
    @staticmethod
    def create_provider(provider_type: str, config: Config) -> 'LLMProvider':
        """Factory method to create LLM providers"""
        if provider_type.lower() == 'google':
            from .google_provider import GoogleProvider
            return GoogleProvider(config)
        elif provider_type.lower() == 'openai':
            from .openai_provider import OpenAIProvider
            return OpenAIProvider(config)
        elif provider_type.lower() == 'groq':
            from .groq_provider import GroqProvider
            return GroqProvider(config)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_type}")