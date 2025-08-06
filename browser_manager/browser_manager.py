"""Browser management for BrowserTest AI"""

import asyncio
from typing import Dict, Any, Optional, List

from config.config import Config


class BrowserManager:
    """Manages browser configuration and settings"""
    
    def __init__(self, config: Config):
        """Initialize browser manager
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.active_sessions: Dict[str, Any] = {}
        
    def get_browser_config(self, browser_type: Optional[str] = None) -> Dict[str, Any]:
        """Get browser configuration for Agent initialization
        
        Args:
            browser_type: Type of browser (chrome, firefox, etc.)
            
        Returns:
            Browser configuration dictionary
        """
        return {
            "headless": self.config.get("browser.headless", False),
            "viewport": {
                "width": self.config.get("browser.viewport.width", 1920),
                "height": self.config.get("browser.viewport.height", 1080)
            },
            "user_data_dir": self.config.get("browser.user_data_dir"),
            "downloads_path": self.config.get("browser.downloads_path", "./downloads")
        }
        
    def register_session(self, session_id: str, agent: Any):
        """Register an active browser session
        
        Args:
            session_id: Unique session identifier
            agent: Browser-use Agent instance
        """
        self.active_sessions[session_id] = agent
    
    def unregister_session(self, session_id: str):
        """Unregister a browser session
        
        Args:
            session_id: Session identifier to remove
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    async def cleanup(self):
        """Cleanup all resources"""
        # Browser cleanup is now handled by individual agents
        self.active_sessions.clear()
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active browser session keys
        
        Returns:
            List of active session keys
        """
        return list(self.active_sessions.keys())
    
    def get_session_count(self) -> int:
        """Get number of active browser sessions
        
        Returns:
            Number of active sessions
        """
        return len(self.active_sessions)
    
    def get_browser_types(self) -> List[str]:
        """Get supported browser types
        
        Returns:
            List of supported browser types
        """
        return ["chrome", "firefox", "safari", "edge"]