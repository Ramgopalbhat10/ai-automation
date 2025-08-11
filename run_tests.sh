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
    echo "  install                      - Install dependencies"
    echo "  test                         - Run all tests"
    echo "  test-unit                    - Run unit tests only"
    echo "  test-integration             - Run integration tests only"
    echo "  test-yaml                    - Run YAML suite tests"
    echo "  test-all                     - Run all tests with report generation"
    echo "  test-and-serve               - Run tests and start allure server"
    echo "  quick-test                   - Run quick test with default suite"
    echo "  test-parallel                - Run tests in parallel"
    echo "  clean                        - Clean test results and reports"
    echo "  clean-preserve-history       - Clean results but preserve test history"
    echo "  preserve-history             - Copy history from previous report"
    echo "  generate-report              - Generate allure HTML report (no history)"
    echo "  generate-report-with-history - Generate allure HTML report with history"
    echo "  generate-timestamped-report  - Generate timestamped report for archival"
    echo "  archive-results              - Archive current test results"
    echo "  serve-report                 - Start allure server"
    echo "  list-suites                  - List available YAML test suites"
    echo "  ci-test                      - Run CI tests with report"
    echo "  ci-test-yaml                 - Run CI YAML tests with report"
    echo "  test-with-history [type]     - Complete automated workflow with history management"
    echo
    echo "History Management:"
    echo "  For proper test history tracking, use these commands in sequence:"
    echo "  1. ./run_tests.sh preserve-history     (before running new tests)"
    echo "  2. ./run_tests.sh test-yaml            (run your tests)"
    echo "  3. ./run_tests.sh generate-report-with-history (generate report with history)"
    echo
    echo "Examples:"
    echo "  ./run_tests.sh test-yaml"
    echo "  ./run_tests.sh test-and-serve"
    echo "  ./run_tests.sh test-parallel"
    echo "  ./run_tests.sh clean-preserve-history"
    echo "  ./run_tests.sh generate-report-with-history"
    echo "  ./run_tests.sh test-with-history yaml"
    echo "  ./run_tests.sh test-with-history parallel"
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

# Preserve history from previous report
preserve_history() {
    print_info "Preserving test history..."
    if [ -d "allure-report/history" ]; then
        mkdir -p allure-results
        # Remove existing history in results to avoid conflicts
        rm -rf allure-results/history 2>/dev/null || true
        cp -r allure-report/history allure-results/
        print_success "History preserved from allure-report/history to allure-results/history"
    else
        print_info "No previous history found in allure-report/history"
    fi
}

# Clean results but preserve history
clean_results_preserve_history() {
    print_info "Cleaning test results while preserving history..."
    # Preserve history before cleaning
    preserve_history
    # Remove only the allure-results content, not the history
    if [ -d "allure-results" ]; then
        find allure-results -type f ! -path "allure-results/history/*" -delete 2>/dev/null || true
        find allure-results -type d -empty ! -path "allure-results/history*" -delete 2>/dev/null || true
    fi
    # DO NOT remove allure-report here - it contains history we need
    rm -rf .pytest_cache
    rm -f reports/*.html reports/*.md 2>/dev/null || true
    print_success "Cleanup completed with history preserved!"
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

# Generate report with history preservation
generate_report_with_history() {
    print_info "Generating allure HTML report with history..."
    if [ ! -d "allure-results" ]; then
        print_error "No allure results found. Run tests first."
        exit 1
    fi
    
    # Copy history from previous report to results directory (Allure documentation workflow)
    if [ -d "allure-report/history" ]; then
        print_info "Copying history from previous report to results directory..."
        mkdir -p allure-results
        cp -r allure-report/history allure-results/
        print_success "History copied from allure-report/history to allure-results/history"
    else
        print_info "No previous history found in allure-report/history"
    fi
    
    # Generate report with --clean to overwrite existing report
    allure generate allure-results -o allure-report --clean
    print_success "Report with history generated: allure-report/index.html"
}

# Generate timestamped report for archival
generate_timestamped_report() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local archive_dir="allure-reports-archive"
    
    print_info "Generating timestamped report..."
    if [ ! -d "allure-results" ]; then
        print_error "No allure results found. Run tests first."
        exit 1
    fi
    
    mkdir -p "$archive_dir"
    allure generate allure-results -o "$archive_dir/allure-report-$timestamp"
    print_success "Timestamped report generated: $archive_dir/allure-report-$timestamp/index.html"
}

# Archive current results with timestamp
archive_results() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local archive_dir="allure-results-archive"
    
    print_info "Archiving current test results..."
    if [ ! -d "allure-results" ]; then
        print_error "No allure results found to archive."
        exit 1
    fi
    
    mkdir -p "$archive_dir"
    cp -r allure-results "$archive_dir/allure-results-$timestamp"
    print_success "Results archived: $archive_dir/allure-results-$timestamp"
}

# Complete automated workflow with history management
test_with_history_workflow() {
    local test_type="${1:-yaml}"
    
    print_info "Starting automated test workflow with history management..."
    print_info "Test type: $test_type"
    
    # Step 1: Preserve history from previous report
    print_info "Step 1/6: Preserving test history..."
    preserve_history
    
    # Step 2: Clean results but preserve history
    print_info "Step 2/6: Cleaning old results while preserving history..."
    clean_results_preserve_history
    
    # Step 3: Run tests based on type
    print_info "Step 3/6: Running tests..."
    case "$test_type" in
        "yaml")
            run_yaml_tests
            ;;
        "all")
            run_all_tests
            ;;
        "unit")
            run_unit_tests
            ;;
        "integration")
            run_integration_tests
            ;;
        "parallel")
            run_parallel_tests
            ;;
        "quick")
            run_quick_test
            ;;
        *)
            print_info "Unknown test type '$test_type', defaulting to YAML tests"
            run_yaml_tests
            ;;
    esac
    
    # Check if tests ran successfully
    if [ $? -ne 0 ]; then
        print_info "Tests completed with some failures, but continuing with report generation..."
    fi
    
    # Step 4: Generate report with history
    print_info "Step 4/6: Generating report with history..."
    generate_report_with_history
    
    # Step 5: Create timestamped archive (optional)
    print_info "Step 5/6: Creating timestamped archive..."
    generate_timestamped_report
    
    # Step 6: Start allure server
    print_info "Step 6/6: Starting Allure server..."
    print_success "🎉 Automated workflow completed successfully!"
    print_info "Report available at: allure-report/index.html"
    print_info "Starting server for immediate viewing..."
    
    # Start the server
    serve_report
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
    generate_report_with_history
    print_success "CI tests completed!"
}

run_ci_yaml_tests() {
    print_info "Running CI YAML tests..."
    export YAML_SUITE="$SUITE"
    python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite" --tb=short --strict-markers
    generate_report_with_history
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
    "clean-preserve-history")
        clean_results_preserve_history
        ;;
    "preserve-history")
        preserve_history
        ;;
    "generate-report-with-history")
        generate_report_with_history
        ;;
    "generate-timestamped-report")
        generate_timestamped_report
        ;;
    "archive-results")
        archive_results
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
    "test-with-history")
        test_with_history_workflow "$2"
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac