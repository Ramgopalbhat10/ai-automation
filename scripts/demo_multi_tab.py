#!/usr/bin/env python3
"""
Multi-Tab Browser Demonstration
Shows how the BrowserTest AI framework handles multiple tabs within the same browser.

This script demonstrates the browser-use library's capabilities for:
1. Opening multiple tabs in the same browser instance
2. Running parallel agents in different tabs
3. Sequential tab management and reuse
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from browser_use import Agent, BrowserSession
from browser_use.llm import ChatOpenAI
from playwright.async_api import async_playwright
from config.config import Config
from llm_integration.llm_provider import LLMProvider


async def demo_parallel_tabs():
    """
    Demonstrate parallel execution in multiple tabs of the same browser.
    This is ideal for independent tasks that don't interfere with each other.
    """
    print("🚀 Demo: Parallel Agents in Multiple Tabs")
    print("="*50)
    
    async with async_playwright() as playwright:
        # Launch browser with persistent context
        browser_context = await playwright.chromium.launch_persistent_context(
            user_data_dir=None,  # Use temporary directory
            headless=False,
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Create multiple pages (tabs)
        page1 = await browser_context.new_page()
        page2 = await browser_context.new_page()
        page3 = await browser_context.new_page()
        
        print(f"📱 Created 3 tabs in the same browser")
        
        # Initialize LLM (you'll need to set up your API key)
        config = Config()
        llm_provider = LLMProvider.create_provider(config)
        llm = await llm_provider.get_llm()
        
        # Create agents for each tab with different tasks
        agent1 = Agent(
            task="Navigate to https://mrgb.in and describe what you see on the homepage. Focus on the main heading, description, and navigation elements.",
            llm=llm,
            page=page1,
        )
        
        agent2 = Agent(
            task="Navigate to https://mrgb.in/blog and list all the blog posts you can find. Describe their titles and any visible content.",
            llm=llm,
            page=page2,
        )
        
        agent3 = Agent(
            task="Navigate to https://mrgb.in/work and describe the work experience information displayed on the page.",
            llm=llm,
            page=page3,
        )
        
        print("🔄 Running 3 agents in parallel...")
        
        # Run all agents in parallel
        results = await asyncio.gather(
            agent1.run(),
            agent2.run(),
            agent3.run(),
            return_exceptions=True
        )
        
        # Display results
        print("\n📊 Results:")
        print("-" * 30)
        
        tasks = ["Homepage Analysis", "Blog Section", "Work Experience"]
        for i, (task, result) in enumerate(zip(tasks, results)):
            print(f"\n{i+1}. {task}:")
            if isinstance(result, Exception):
                print(f"   ❌ Error: {str(result)}")
            else:
                print(f"   ✅ Success: {str(result)[:200]}...")
        
        await browser_context.close()
        print("\n🔒 Browser closed")


async def demo_sequential_tab_reuse():
    """
    Demonstrate sequential execution with tab reuse.
    This approach is more resource-efficient for related tasks.
    """
    print("\n🔄 Demo: Sequential Execution with Tab Reuse")
    print("="*50)
    
    # Create a reusable browser session
    browser_session = BrowserSession(
        headless=False,
        viewport={'width': 1920, 'height': 1080},
        keep_alive=True  # Keep browser alive between tasks
    )
    
    try:
        await browser_session.start()
        print("📱 Browser session started")
        
        # Initialize LLM
        config = Config()
        llm_provider = LLMProvider.create_provider(config)
        llm = await llm_provider.get_llm()
        
        # Sequential tasks that build on each other
        tasks = [
            {
                'name': 'Homepage Navigation',
                'task': 'Navigate to https://mrgb.in and verify the page loads correctly. Take note of the navigation menu.',
                'url': 'https://mrgb.in'
            },
            {
                'name': 'Blog Navigation',
                'task': 'Click on the blog link in the navigation menu and verify you reach the blog section. Count how many blog posts are visible.',
                'url': None  # Will use navigation from previous page
            },
            {
                'name': 'Work Navigation',
                'task': 'Navigate to the work section and read the work experience information. Then return to the homepage.',
                'url': None  # Will use navigation from current page
            }
        ]
        
        results = []
        for i, task_info in enumerate(tasks):
            print(f"\n📝 Task {i+1}: {task_info['name']}")
            
            # Navigate to URL if specified
            if task_info['url']:
                page = await browser_session.get_current_page()
                await page.goto(task_info['url'])
            
            # Create and run agent
            agent = Agent(
                task=task_info['task'],
                llm=llm,
                browser_session=browser_session
            )
            
            try:
                result = await agent.run()
                results.append(f"✅ {task_info['name']}: Success")
                print(f"   Result: {str(result)[:150]}...")
            except Exception as e:
                results.append(f"❌ {task_info['name']}: {str(e)}")
                print(f"   Error: {str(e)}")
        
        print("\n📊 Sequential Execution Summary:")
        for result in results:
            print(f"   {result}")
            
    finally:
        await browser_session.close()
        print("\n🔒 Browser session closed")


async def demo_tab_management():
    """
    Demonstrate advanced tab management capabilities.
    Shows how to create, switch between, and manage multiple tabs.
    """
    print("\n🗂️  Demo: Advanced Tab Management")
    print("="*50)
    
    browser_session = BrowserSession(
        headless=False,
        keep_alive=True
    )
    
    try:
        await browser_session.start()
        
        # Get the browser context for tab management
        context = browser_session.browser_context
        
        # Create multiple tabs with different URLs
        urls = [
            'https://mrgb.in',
            'https://mrgb.in/blog',
            'https://mrgb.in/work'
        ]
        
        tabs = []
        for i, url in enumerate(urls):
            page = await context.new_page()
            await page.goto(url)
            tabs.append(page)
            print(f"📄 Tab {i+1}: Opened {url}")
        
        # Demonstrate tab switching and information gathering
        print("\n🔍 Gathering information from all tabs:")
        
        for i, page in enumerate(tabs):
            await page.bring_to_front()
            title = await page.title()
            url = page.url
            print(f"   Tab {i+1}: '{title}' at {url}")
        
        # Close specific tabs
        print("\n🗑️  Closing blog and work tabs, keeping homepage...")
        await tabs[1].close()  # Close blog tab
        await tabs[2].close()  # Close work tab
        
        # Verify remaining tab
        remaining_pages = context.pages
        print(f"   Remaining tabs: {len(remaining_pages)}")
        
    finally:
        await browser_session.close()
        print("\n🔒 All tabs and browser closed")


async def main():
    """
    Run all demonstrations to show multi-tab capabilities.
    """
    print("🎯 BrowserTest AI - Multi-Tab Capabilities Demo")
    print("Testing with https://mrgb.in")
    print("=" * 60)
    
    try:
        # Demo 1: Parallel execution in multiple tabs
        await demo_parallel_tabs()
        
        # Demo 2: Sequential execution with tab reuse
        await demo_sequential_tab_reuse()
        
        # Demo 3: Advanced tab management
        await demo_tab_management()
        
        print("\n🎉 All demonstrations completed successfully!")
        print("\n💡 Key Takeaways:")
        print("   ✅ Browser-use supports multiple tabs in the same browser")
        print("   ✅ Parallel execution is possible with different tabs")
        print("   ✅ Sequential execution can reuse browser sessions efficiently")
        print("   ✅ Advanced tab management provides fine-grained control")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("⚠️  Note: Make sure you have set up your LLM API key (GOOGLE_API_KEY or OPENAI_API_KEY)")
    print("   This demo will open a browser and navigate to https://mrgb.in\n")
    
    asyncio.run(main())