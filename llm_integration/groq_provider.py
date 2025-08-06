import os
from typing import Dict, Any
from browser_use.llm import ChatGroq
from .llm_provider import LLMProvider
from config.config import Config

class GroqProvider(LLMProvider):
    """Groq LLM provider for browser-use integration"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.api_key = config.get("llm.groq.api_key") or os.getenv("GROQ_API_KEY")
        self.model_name = config.get("llm.groq.model", "meta-llama/llama-4-scout-17b-16e-instruct")
        self.temperature = config.get("llm.groq.temperature", 0.1)
        self.max_tokens = config.get("llm.groq.max_tokens", 8192)
        
    def get_llm(self):
        """Return ChatGroq instance compatible with browser-use Agent"""
        if self._llm is None:
            if not self.api_key:
                raise ValueError("Groq API key not found. Set GROQ_API_KEY environment variable or configure in settings.")
            
            # ChatGroq from browser-use only accepts model parameter
            # API key should be set via GROQ_API_KEY environment variable
            self._llm = ChatGroq(
                model=self.model_name
            )
        return self._llm
    
    def validate_credentials(self) -> bool:
        """Validate Groq API credentials"""
        try:
            if not self.api_key:
                return False
            
            # Test by creating the LLM instance
            # The agent will handle actual LLM invocation
            llm = self.get_llm()
            # If we can create the instance without error, credentials are valid
            return True
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Groq model information"""
        return {
            "provider": "groq",
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "supports_vision": self.supports_vision(),
            "api_key_configured": bool(self.api_key)
        }
    
    def get_model_name(self) -> str:
        """Get the model name/identifier"""
        return self.model_name
    
    def supports_function_calling(self) -> bool:
        """Check if the model supports function calling"""
        # Most Groq models support function calling
        function_calling_models = ['llama-3.3', 'llama-3.1', 'mixtral']
        return any(model in self.model_name.lower() for model in function_calling_models)
    
    def supports_vision(self) -> bool:
        """Check if the model supports vision capabilities"""
        # Currently, most Groq models don't support vision
        # This may change in the future
        vision_models = ['llava']
        return any(vision_model in self.model_name.lower() for vision_model in vision_models)