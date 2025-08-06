import os
from typing import Dict, Any
from browser_use.llm import ChatOpenAI
from .llm_provider import LLMProvider
from config.config import Config

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider for browser-use integration"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.base_url = config.get("llm.openai.base_url") # For custom endpoints
        self.api_key = config.get("llm.openai.api_key") or os.getenv("OPENAI_API_KEY")
        self.model_name = config.get("llm.openai.model", "meta-llama/Llama-4-Scout-17B-16E-Instruct")
        self.temperature = config.get("llm.openai.temperature", 0.1)
        
    def get_llm(self):
        """Return ChatOpenAI instance compatible with browser-use Agent"""
        if self._llm is None:
            if not self.api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or configure in settings.")
            
            kwargs = {
                "model": self.model_name,
                "api_key": self.api_key,
                "temperature": self.temperature
            }
            
            # Add base_url if configured (for custom endpoints)
            if self.base_url:
                kwargs["base_url"] = self.base_url
            
            self._llm = ChatOpenAI(**kwargs)
        return self._llm
    
    def validate_credentials(self) -> bool:
        """Validate OpenAI API credentials"""
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
        """Get OpenAI model information"""
        return {
            "provider": "openai",
            "model": self.model_name,
            "temperature": self.temperature,
            "supports_vision": self.supports_vision(),
            "api_key_configured": bool(self.api_key),
            "base_url": self.base_url
        }
    
    def get_model_name(self) -> str:
        """Get the model name/identifier"""
        return self.model_name
    
    def supports_function_calling(self) -> bool:
        """Check if the model supports function calling"""
        # GPT-4 and GPT-3.5-turbo models support function calling
        function_calling_models = ["gpt-4", "gpt-3.5-turbo"]
        return any(model in self.model_name.lower() for model in function_calling_models)
    
    def is_vision_model(self) -> bool:
        """Check if this is specifically a vision-enabled model"""
        vision_indicators = ["gpt-4o", "gpt-4-vision", "vision"]
        return any(indicator in self.model_name.lower() for indicator in vision_indicators)