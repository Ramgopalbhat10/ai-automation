#!/usr/bin/env python3
"""Pytest runner script with allure integration for BrowserTest AI"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def run_pytest_with_allure(args):
    """Run pytest with allure reporting"""
    project_root = Path(__file__).parent
    
    # Base pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--alluredir=allure-results",
        "-v",
        "--tb=short"
    ]
    
    # Add YAML suite if specified
    if args.yaml_suite:
        yaml_path = args.yaml_suite
        if not os.path.isabs(yaml_path):
            yaml_path = os.path.join(project_root, yaml_path)
        cmd.extend(["--yaml-suite", yaml_path])
    
    # Add browser option
    if args.browser:
        cmd.extend(["--browser", args.browser])
    
    # Add headless option
    if args.headless:
        cmd.append("--headless")
    
    # Add markers filter
    if args.markers:
        cmd.extend(["-m", args.markers])
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add custom pytest args
    if args.pytest_args:
        cmd.extend(args.pytest_args.split())
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Set environment variables
    env = os.environ.copy()
    if args.yaml_suite:
        env["YAML_SUITE"] = yaml_path
    
    # Run pytest
    result = subprocess.run(cmd, cwd=project_root, env=env)
    
    if result.returncode == 0:
        print("\n✅ Tests completed successfully!")
        
        # Generate allure report if requested
        if args.generate_report:
            generate_allure_report(project_root)
    else:
        print("\n❌ Tests failed!")
        if args.generate_report:
            print("Generating allure report for failed tests...")
            generate_allure_report(project_root)
    
    return result.returncode


def generate_allure_report(project_root):
    """Generate allure HTML report"""
    allure_results = project_root / "allure-results"
    allure_report = project_root / "allure-report"
    
    if not allure_results.exists():
        print("❌ No allure results found. Run tests first.")
        return
    
    try:
        # Check if allure is installed
        subprocess.run(["allure", "--version"], check=True, capture_output=True)
        
        # Generate report
        cmd = ["allure", "generate", str(allure_results), "-o", str(allure_report), "--clean"]
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n📊 Allure report generated: {allure_report / 'index.html'}")
            print(f"To view the report, run: allure open {allure_report}")
        else:
            print(f"❌ Failed to generate allure report: {result.stderr}")
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Allure CLI not found. Install it with: npm install -g allure-commandline")
        print("   Or download from: https://github.com/allure-framework/allure2/releases")


def serve_allure_report(project_root):
    """Serve allure report"""
    allure_report = project_root / "allure-report"
    
    if not allure_report.exists():
        print("❌ No allure report found. Generate it first with --generate-report")
        return 1
    
    try:
        cmd = ["allure", "open", str(allure_report)]
        subprocess.run(cmd, cwd=project_root)
    except FileNotFoundError:
        print("❌ Allure CLI not found. Install it with: npm install -g allure-commandline")
        return 1
    
    return 0


def list_available_suites(project_root):
    """List available YAML test suites"""
    suites_dir = project_root / "test_suites"
    
    if not suites_dir.exists():
        print("❌ No test_suites directory found")
        return
    
    print("📋 Available YAML test suites:")
    print("=" * 40)
    
    for yaml_file in suites_dir.rglob("*.yaml"):
        relative_path = yaml_file.relative_to(project_root)
        print(f"  {relative_path}")
    
    for yml_file in suites_dir.rglob("*.yml"):
        relative_path = yml_file.relative_to(project_root)
        print(f"  {relative_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run BrowserTest AI tests with pytest and allure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests with default suite
  python run_pytest.py
  
  # Run specific test suite
  python run_pytest.py --yaml-suite test_suites/production/mrgb_blog_test_suite.yaml
  
  # Run tests in headless mode and generate report
  python run_pytest.py --headless --generate-report
  
  # Run only browser tests
  python run_pytest.py --markers "browser"
  
  # List available test suites
  python run_pytest.py --list-suites
  
  # Serve existing allure report
  python run_pytest.py --serve-report
"""
    )
    
    parser.add_argument(
        "--yaml-suite",
        help="Path to YAML test suite file"
    )
    
    parser.add_argument(
        "--browser",
        choices=["chrome", "firefox", "safari", "edge"],
        default="chrome",
        help="Browser to use for testing (default: chrome)"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    
    parser.add_argument(
        "--markers",
        help="Pytest markers to filter tests (e.g., 'browser', 'not slow')"
    )
    
    parser.add_argument(
        "--parallel",
        type=int,
        help="Number of parallel workers (requires pytest-xdist)"
    )
    
    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Generate allure HTML report after tests"
    )
    
    parser.add_argument(
        "--serve-report",
        action="store_true",
        help="Serve existing allure report"
    )
    
    parser.add_argument(
        "--list-suites",
        action="store_true",
        help="List available YAML test suites"
    )
    
    parser.add_argument(
        "--pytest-args",
        help="Additional pytest arguments (as a single quoted string)"
    )
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent
    
    # Handle special commands
    if args.list_suites:
        list_available_suites(project_root)
        return 0
    
    if args.serve_report:
        return serve_allure_report(project_root)
    
    # Run tests
    return run_pytest_with_allure(args)


if __name__ == "__main__":
    sys.exit(main())