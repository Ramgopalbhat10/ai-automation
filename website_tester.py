#!/usr/bin/env python3
"""
Website Testing Automation Script using browser-use library

This script allows you to test websites by providing simple prompts.
Example usage: Test windsurf.com blog for articles about "Wave 11"
"""

import asyncio
import os
from typing import Optional
from dotenv import load_dotenv
from browser_use import Agent
from browser_use.llm import ChatGoogle

class WebsiteTester:
    """A simple website testing automation class using browser-use library."""
    
    def __init__(self, api_key: Optional[str] = None, headless: bool = False):
        """
        Initialize the website tester.
        
        Args:
            api_key: OpenAI API key (if not provided, will try to get from environment)
            headless: Whether to run browser in headless mode
        """
        # Load environment variables
        load_dotenv()
        
        # Check if Google API key is set
        if not os.getenv('GOOGLE_API_KEY'):
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in your .env file.")
        
        # Initialize the language model
        self.llm = ChatGoogle(
            model="gemini-2.5-flash-lite",
            temperature=0.1
        )
        
        # Store headless setting
        self.headless = headless
    
    async def test_website(self, prompt: str) -> str:
        """
        Test a website based on the given prompt.
        
        Args:
            prompt: Natural language description of what to test
            
        Returns:
            Result of the test as a string
        """
        try:
            # Create browser agent
            agent = Agent(
                task=prompt,
                llm=self.llm,
                headless=self.headless
            )
            
            # Run the automation task
            result = await agent.run()
            
            return str(result)
            
        except Exception as e:
            return f"Error during website testing: {str(e)}"
    
    async def test_windsurf_blog(self, search_term: str = "Wave 11") -> str:
        """
        Specific test for windsurf.com blog to search for articles.
        
        Args:
            search_term: Term to search for in the blog
            
        Returns:
            Result of the search
        """
        prompt = f"""
        Go to windsurf.com website and navigate to their blog section.
        Search for articles or content related to "{search_term}".
        If you find any articles about {search_term}, extract the title, date, and a brief summary.
        If no articles are found, report that no content about {search_term} was found.
        """
        
        return await self.test_website(prompt)
    
    async def custom_test(self, website_url: str, action_description: str) -> str:
        """
        Perform a custom test on any website.
        
        Args:
            website_url: URL of the website to test
            action_description: Description of what actions to perform
            
        Returns:
            Result of the test
        """
        prompt = f"""
        Go to {website_url} and {action_description}
        Provide a detailed report of what you found and any issues encountered.
        """
        
        return await self.test_website(prompt)


async def main():
    """Main function to demonstrate the website tester."""
    print("Website Testing Automation Script")
    print("=" * 40)
    
    # Initialize tester
    tester = WebsiteTester(headless=False)
    
    while True:
        print("\nChoose an option:")
        print("1. Test windsurf.com blog for Wave 11 articles")
        print("2. Custom website test")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\nTesting windsurf.com blog for Wave 11 articles...")
            result = await tester.test_windsurf_blog()
            print("\nResult:")
            print("-" * 20)
            print(result)
            
        elif choice == "2":
            website_url = input("Enter website URL: ").strip()
            action_description = input("Describe what you want to test: ").strip()
            
            print(f"\nTesting {website_url}...")
            result = await tester.custom_test(website_url, action_description)
            print("\nResult:")
            print("-" * 20)
            print(result)
            
        elif choice == "3":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Check if Google API key is set before running
    load_dotenv()
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
        print("Please add your Google API key to the .env file:")
        print("GOOGLE_API_KEY=your_api_key_here")
        exit(1)
    
    asyncio.run(main())