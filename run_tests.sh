#!/bin/bash
# BrowserTest AI - Test Runner for Unix/Linux/Git Bash
# This script provides Makefile-like functionality

set -e  # Exit on any error

# Default values
SUITE=${SUITE:-"test_suites/production/mrgb_blog_test_suite.yaml"}
BROWSER=${BROWSER:-"chrome"}
HEADLESS=${HEADLESS:-"true"}
MARKERS=${MARKERS:-""}
PARALLEL=${PARALLEL:-"2"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}BrowserTest AI - Pytest & Allure Integration${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

show_help() {
    print_header
    echo "Available commands:"
    echo "  install          - Install dependencies"
    echo "  test             - Run all tests"
    echo "  test-unit        - Run unit tests only"
    echo "  test-integration - Run integration tests only"
    echo "  test-yaml        - Run YAML suite tests"
    echo "  test-all         - Run all tests with report generation"
    echo "  test-and-serve   - Run tests and start allure server"
    echo "  quick-test       - Run quick test with default suite"
    echo "  test-parallel    - Run tests in parallel"
    echo "  clean-results    - Clean test results and reports"
    echo "  generate-report  - Generate allure HTML report"
    echo "  serve-report     - Start allure server"
    echo "  list-suites      - List available YAML test suites"
    echo "  ci-test          - Run CI tests with report"
    echo "  ci-test-yaml     - Run CI YAML tests with report"
    echo
    echo "Examples:"
    echo "  ./run_tests.sh test-yaml"
    echo "  ./run_tests.sh test-and-serve"
    echo "  ./run_tests.sh test-parallel"
    echo "  SUITE=test_suites/dev/example.yaml ./run_tests.sh test-yaml"
    echo
    echo "Environment Variables:"
    echo "  SUITE    - Test suite file (default: test_suites/production/mrgb_blog_test_suite.yaml)"
    echo "  BROWSER  - Browser to use (default: chrome)"
    echo "  HEADLESS - Run in headless mode (default: true)"
    echo "  MARKERS  - Pytest markers to filter tests"
    echo "  PARALLEL - Number of parallel workers (default: 2)"
}

install_deps() {
    print_info "Installing dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies installed successfully!"
}

run_all_tests() {
    print_info "Running all tests..."
    python -m pytest tests/ -v --alluredir=allure-results
    print_success "All tests completed!"
}

run_unit_tests() {
    print_info "Running unit tests..."
    python -m pytest tests/ -v --alluredir=allure-results -m "unit"
    print_success "Unit tests completed!"
}

run_integration_tests() {
    print_info "Running integration tests..."
    python -m pytest tests/ -v --alluredir=allure-results -m "integration"
    print_success "Integration tests completed!"
}

run_yaml_tests() {
    print_info "Running YAML suite tests..."
    print_info "Using test suite: $SUITE"
    export YAML_SUITE="$SUITE"
    python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite"
    print_success "YAML tests completed!"
}

run_all_with_report() {
    print_info "Running all tests with report generation..."
    run_all_tests
    generate_report
    print_success "All tests completed with report generation!"
}

run_test_and_serve() {
    print_info "Running tests and starting allure server..."
    run_yaml_tests
    generate_report
    print_info "Tests completed! Starting allure server..."
    allure serve allure-results
}

run_quick_test() {
    print_info "Running quick test with default suite..."
    export YAML_SUITE="$SUITE"
    python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite"
    print_success "Quick test completed!"
}

run_parallel_tests() {
    print_info "Running tests in parallel..."
    export YAML_SUITE="$SUITE"
    python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite" -n "$PARALLEL"
    print_success "Parallel tests completed!"
}

clean_results() {
    print_info "Cleaning test results and reports..."
    rm -rf allure-results allure-report .pytest_cache
    rm -f reports/*.html reports/*.md 2>/dev/null || true
    print_success "Cleanup completed!"
}

generate_report() {
    print_info "Generating allure HTML report..."
    if [ ! -d "allure-results" ]; then
        print_error "No allure results found. Run tests first."
        exit 1
    fi
    allure generate allure-results -o allure-report --clean
    print_success "Report generated: allure-report/index.html"
}

serve_report() {
    print_info "Starting allure server..."
    allure serve allure-results
}

list_suites() {
    print_info "Listing available YAML test suites..."
    find test_suites -name "*.yaml" -type f | sort
}

run_ci_tests() {
    print_info "Running CI tests..."
    python -m pytest tests/ -v --alluredir=allure-results --tb=short --strict-markers
    generate_report
    print_success "CI tests completed!"
}

run_ci_yaml_tests() {
    print_info "Running CI YAML tests..."
    export YAML_SUITE="$SUITE"
    python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite" --tb=short --strict-markers
    generate_report
    print_success "CI YAML tests completed!"
}

# Main command dispatcher
case "$1" in
    "")
        show_help
        ;;
    "help")
        show_help
        ;;
    "install")
        install_deps
        ;;
    "test")
        run_all_tests
        ;;
    "test-unit")
        run_unit_tests
        ;;
    "test-integration")
        run_integration_tests
        ;;
    "test-yaml")
        run_yaml_tests
        ;;
    "test-all")
        run_all_with_report
        ;;
    "test-and-serve")
        run_test_and_serve
        ;;
    "quick-test")
        run_quick_test
        ;;
    "test-parallel")
        run_parallel_tests
        ;;
    "clean-results")
        clean_results
        ;;
    "generate-report")
        generate_report
        ;;
    "serve-report")
        serve_report
        ;;
    "list-suites")
        list_suites
        ;;
    "ci-test")
        run_ci_tests
        ;;
    "ci-test-yaml")
        run_ci_yaml_tests
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac