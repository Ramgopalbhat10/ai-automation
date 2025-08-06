import asyncio
from typing import Dict, Any, Optional, List
from browser_use import Agent
from .llm_provider import LLMProvider
from config.config import Config

class BrowserUseIntegration:
    """Integration layer for browser-use library with Agent management"""
    
    def __init__(self, config: Config, llm_provider: LLMProvider):
        self.config = config
        self.llm_provider = llm_provider
        self.current_agent: Optional[Agent] = None
        
    def get_browser_config(self) -> Dict[str, Any]:
        """Get browser configuration for Agent initialization"""
        return {
            "headless": self.config.get("browser.headless", False),
            "viewport": {
                "width": self.config.get("browser.viewport.width", 1920),
                "height": self.config.get("browser.viewport.height", 1080)
            },
            "user_data_dir": self.config.get("browser.user_data_dir"),
            "downloads_path": self.config.get("browser.downloads_path", "./downloads")
        }
    
    async def create_agent(
        self,
        task: str,
        use_vision: Optional[bool] = None,
        max_steps: Optional[int] = None,
        **kwargs
    ) -> Agent:
        """Create an Agent instance with the configured LLM"""
        
        # Get LLM instance from provider
        llm = self.llm_provider.get_llm()
        
        # Set vision capability
        if use_vision is None:
            use_vision = self.llm_provider.supports_vision()
        
        # Get browser configuration
        browser_config = self.get_browser_config()
        
        # Create agent with current API
        agent = Agent(
            task=task,
            llm=llm,
            use_vision=use_vision,
            max_steps=max_steps or self.config.get("browser.max_steps", 100),
            **browser_config
        )
        
        self.current_agent = agent
        return agent
    
    async def run_agent(
        self,
        task: str,
        **kwargs
    ) -> Any:
        """Create and run an agent with the given task"""
        agent = await self.create_agent(task, **kwargs)
        result = await agent.run()
        return result
    
    async def run_parallel_agents(
        self,
        tasks: List[str],
        **kwargs
    ) -> List[Any]:
        """Run multiple agents in parallel"""
        agents = []
        for task in tasks:
            agent = await self.create_agent(task, **kwargs)
            agents.append(agent)
        
        # Run all agents concurrently
        results = await asyncio.gather(
            *[agent.run() for agent in agents],
            return_exceptions=True
        )
        
        return results
    
    def get_agent_configuration(self) -> Dict[str, Any]:
        """Get current agent configuration"""
        return {
            "llm_provider": self.llm_provider.get_model_info(),
            "browser_config": self.get_browser_config(),
            "supports_vision": self.llm_provider.supports_vision()
        }
    
    async def cleanup(self):
        """Clean up browser sessions and resources"""
        if self.current_agent:
            # Browser cleanup is handled by the agent
            self.current_agent = None