#!/usr/bin/env python3
"""
BrowserTest AI - Universal CLI Entry Point

This is the main entry point for running any YAML test suite without requiring
separate Python scripts for each test suite. The core engine handles all
configurations and test types based on the YAML file.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import Config
from config.yaml_loader import YAMLLoader
from test_engine.test_engine import TestEngine
from test_engine.result_collector import ResultCollector


def print_banner():
    """Print application banner"""
    print("\n" + "="*80)
    print("🤖 BrowserTest AI - Universal Test Suite Runner")
    print("   Intelligent browser automation with natural language prompts")
    print("="*80 + "\n")


def validate_yaml_file(file_path: str) -> bool:
    """Validate that the YAML file exists and is valid
    
    Args:
        file_path: Path to YAML file
        
    Returns:
        True if valid, False otherwise
    """
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ Error: Test suite file not found: {file_path}")
            return False
            
        if not path.suffix.lower() in ['.yaml', '.yml']:
            print(f"❌ Error: File must be a YAML file (.yaml or .yml): {file_path}")
            return False
            
        # Try to load and validate the YAML
        YAMLLoader.load_test_suite(file_path)
        print(f"✅ YAML file validated: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error validating YAML file: {e}")
        return False


def list_available_test_suites():
    """List all available test suites in the project"""
    print("📋 Available Test Suites:\n")
    
    test_suites_dir = project_root / "test_suites"
    if not test_suites_dir.exists():
        print("   No test_suites directory found.")
        return
    
    found_suites = False
    
    for env_dir in ["examples", "staging", "production"]:
        env_path = test_suites_dir / env_dir
        if env_path.exists():
            yaml_files = list(env_path.glob("*.yaml")) + list(env_path.glob("*.yml"))
            if yaml_files:
                print(f"   📁 {env_dir.upper()}:")
                for yaml_file in sorted(yaml_files):
                    rel_path = yaml_file.relative_to(project_root)
                    print(f"      • {rel_path}")
                print()
                found_suites = True
    
    if not found_suites:
        print("   No YAML test suites found.")


async def run_test_suite(yaml_file: str, config_overrides: Optional[dict] = None):
    """Run a test suite from YAML file
    
    Args:
        yaml_file: Path to YAML test suite file
        config_overrides: Optional configuration overrides
    """
    try:
        print(f"🔧 Initializing configuration...")
        config = Config()
        
        # Apply any configuration overrides
        if config_overrides:
            for key, value in config_overrides.items():
                config.set(key, value)
        
        print(f"📋 Loading test suite: {yaml_file}")
        test_suite = YAMLLoader.load_test_suite(yaml_file)
        
        # Set base_url from test suite into config if not already set
        if test_suite.base_url and not config.get("base_url"):
            config.set("base_url", test_suite.base_url)
            print(f"🔗 Set base URL from test suite: {test_suite.base_url}")
        
        # Set LLM provider from test suite if specified
        if test_suite.default_llm_provider and not config_overrides.get("llm.provider") if config_overrides else True:
            config.set("llm.provider", test_suite.default_llm_provider)
            print(f"🧠 Set LLM provider from test suite: {test_suite.default_llm_provider}")
        
        print(f"⚙️ Initializing test engine...")
        test_engine = TestEngine(config)
        
        # Display test suite overview
        print("\n📋 TEST SUITE OVERVIEW:")
        print(f"   Name: {test_suite.name}")
        print(f"   Description: {test_suite.description}")
        print(f"   Base URL: {test_suite.base_url}")
        print(f"   Tests: {len(test_suite.tests)}")
        print(f"   Parallel: {test_suite.parallel}")
        if test_suite.parallel:
            print(f"   Max Workers: {test_suite.max_workers}")
        
        print("\n🧪 TESTS TO EXECUTE:")
        for i, test in enumerate(test_suite.tests, 1):
            tags_str = ", ".join(test.tags) if test.tags else "no tags"
            print(f"   {i:2d}. {test.name} ({tags_str})")
        
        print("\n🚀 Starting test execution...")
        print("-" * 80)
        
        # Execute the test suite
        summary = await test_engine.execute_test_suite(test_suite)
        
        # Generate reports
        print("\n📄 GENERATING REPORTS...")
        print("-" * 80)
        
        # Get result collector from test engine
        result_collector = test_engine.result_collector
        
        # Create reports directory
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        
        # Generate base filename from test suite name
        base_name = Path(yaml_file).stem
        
        # Generate HTML report
        html_report_path = report_dir / f"{base_name}_report_{timestamp}.html"
        html_path = result_collector.export_to_html(str(html_report_path))
        print(f"   📄 HTML report: {html_path}")
        
        # Generate Markdown report
        md_report_path = report_dir / f"{base_name}_report_{timestamp}.md"
        md_path = result_collector.export_to_markdown(str(md_report_path))
        print(f"   📄 Markdown report: {md_path}")
        
        # Display results summary
        print("\n📊 EXECUTION SUMMARY:")
        print("-" * 80)
        stats = summary.get('statistics', {})
        print(f"   Total Tests: {stats.get('total_tests', 0)}")
        print(f"   Passed: {stats.get('passed', 0)}")
        print(f"   Failed: {stats.get('failed', 0)}")
        print(f"   Errors: {stats.get('errors', 0)}")
        print(f"   Duration: {summary.get('total_duration', 0):.2f} seconds")
        
        if summary.get('llm_info'):
            llm_info = summary['llm_info']
            print(f"   LLM Provider: {llm_info.get('provider', 'Unknown')}")
            print(f"   Model: {llm_info.get('model', 'Unknown')}")
        
        print(f"\n📁 Reports saved to: {report_dir.absolute()}")
        
        # Cleanup
        await test_engine.cleanup()
        
        # Return appropriate exit code
        stats = summary.get('statistics', {})
        failed_count = stats.get('failed', 0)
        error_count = stats.get('errors', 0)
        
        if failed_count > 0 or error_count > 0:
            if failed_count > 0 and error_count > 0:
                print(f"\n❌ {failed_count} tests failed and {error_count} tests had errors.")
            elif failed_count > 0:
                print(f"\n❌ {failed_count} tests failed.")
            else:
                print(f"\n❌ {error_count} tests had errors.")
            return 1
        else:
            print("\n✅ All tests passed!")
            return 0
            
    except Exception as e:
        print(f"\n❌ Error executing test suite: {e}")
        return 1


def create_template(output_file: str):
    """Create a template YAML test suite
    
    Args:
        output_file: Path where to create the template
    """
    try:
        YAMLLoader.create_template(output_file)
        print(f"✅ Template created: {output_file}")
        print("   Edit the file to customize your test suite.")
    except Exception as e:
        print(f"❌ Error creating template: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="BrowserTest AI - Universal Test Suite Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run test_suites/examples/example_test_suite.yaml
  %(prog)s run test_suites/production/mrgb_blog_test_suite.yaml --parallel
  %(prog)s list
  %(prog)s validate test_suites/examples/example_test_suite.yaml
  %(prog)s template --output my_test_suite.yaml
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a test suite')
    run_parser.add_argument('yaml_file', help='Path to YAML test suite file')
    run_parser.add_argument('--parallel', action='store_true', help='Force parallel execution')
    run_parser.add_argument('--sequential', action='store_true', help='Force sequential execution')
    run_parser.add_argument('--workers', type=int, help='Number of parallel workers')
    run_parser.add_argument('--llm-provider', choices=['google', 'openai', 'groq'], help='LLM provider to use')
    run_parser.add_argument('--browser', choices=['chrome', 'firefox', 'webkit', 'edge'], help='Browser to use')
    run_parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available test suites')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a YAML test suite')
    validate_parser.add_argument('yaml_file', help='Path to YAML test suite file')
    
    # Template command
    template_parser = subparsers.add_parser('template', help='Create a template test suite')
    template_parser.add_argument('--output', '-o', default='template_test_suite.yaml', help='Output file path')
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.command == 'run':
        # Validate YAML file first
        if not validate_yaml_file(args.yaml_file):
            return 1
        
        # Prepare configuration overrides
        config_overrides = {}
        if args.llm_provider:
            config_overrides['llm.provider'] = args.llm_provider
        if args.browser:
            config_overrides['browser.type'] = args.browser
        if args.headless:
            config_overrides['browser.headless'] = True
        if args.workers:
            config_overrides['test.max_workers'] = args.workers
        if args.parallel:
            config_overrides['test.parallel'] = True
        elif args.sequential:
            config_overrides['test.parallel'] = False
        
        # Run the test suite
        return asyncio.run(run_test_suite(args.yaml_file, config_overrides))
        
    elif args.command == 'list':
        list_available_test_suites()
        return 0
        
    elif args.command == 'validate':
        if validate_yaml_file(args.yaml_file):
            print("✅ YAML file is valid!")
            return 0
        else:
            return 1
            
    elif args.command == 'template':
        create_template(args.output)
        return 0
        
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())