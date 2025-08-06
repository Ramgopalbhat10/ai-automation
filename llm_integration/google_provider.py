import os
from typing import Dict, Any
from browser_use.llm import ChatGoogle
from .llm_provider import LLMProvider
from config.config import Config

class GoogleProvider(LLMProvider):
    """Google Gemini LLM provider for browser-use integration"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.api_key = config.get("llm.google.api_key") or os.getenv("GOOGLE_API_KEY")
        self.model_name = config.get("llm.google.model", "gemini-2.5-flash-lite")
        self.temperature = config.get("llm.google.temperature", 0.1)
        
    def get_llm(self):
        """Return ChatGoogle instance compatible with browser-use Agent"""
        if self._llm is None:
            if not self.api_key:
                raise ValueError("Google API key not found. Set GOOGLE_API_KEY environment variable or configure in settings.")
            
            self._llm = ChatGoogle(
                model=self.model_name,
                api_key=self.api_key,
                temperature=self.temperature
            )
        return self._llm
    
    def validate_credentials(self) -> bool:
        """Validate Google API credentials"""
        try:
            if not self.api_key:
                return False
            
            # Test with a simple request
            llm = self.get_llm()
            # Note: In a real implementation, you might want to make a test call
            # For now, we'll assume valid if we can create the instance
            return True
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Google model information"""
        return {
            "provider": "google",
            "model": self.model_name,
            "temperature": self.temperature,
            "supports_vision": self.supports_vision(),
            "api_key_configured": bool(self.api_key)
        }
    
    def get_model_name(self) -> str:
        """Get the model name/identifier"""
        return self.model_name
    
    def supports_function_calling(self) -> bool:
        """Check if the model supports function calling"""
        # Most Gemini models support function calling
        return "gemini" in self.model_name.lower()