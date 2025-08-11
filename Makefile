# Makefile for BrowserTest AI with pytest and allure

.PHONY: help install test test-unit test-integration test-yaml test-all clean-results generate-report serve-report list-suites test-and-serve quick-test test-parallel ci-test ci-test-yaml

# Default target
help:
	@echo "BrowserTest AI - Pytest & Allure Integration"
	@echo "============================================"
	@echo ""
	@echo "Available targets:"
	@echo "  install          - Install dependencies"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-yaml        - Run YAML suite tests"
	@echo "  test-all         - Run all tests with report generation"
	@echo "  test-and-serve   - Run tests and start allure server"
	@echo "  quick-test       - Run quick test with default suite"
	@echo "  test-parallel    - Run tests in parallel"
	@echo "  clean-results    - Clean test results and reports"
	@echo "  generate-report  - Generate allure HTML report"
	@echo "  serve-report     - Start allure server"
	@echo "  list-suites      - List available YAML test suites"
	@echo "  ci-test          - Run CI tests with report"
	@echo "  ci-test-yaml     - Run CI YAML tests with report"
	@echo ""
	@echo "Examples:"
	@echo "  make test-yaml SUITE=test_suites/production/mrgb_blog_test_suite.yaml"
	@echo "  make test-and-serve SUITE=test_suites/staging/example_test_suite.yaml"
	@echo "  make test-parallel SUITE=test_suites/production/mrgb_blog_test_suite.yaml"

# Variables
SUITE ?= test_suites/production/mrgb_blog_test_suite.yaml
BROWSER ?= chrome
HEADLESS ?= false
MARKERS ?= 
PARALLEL ?= 

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Dependencies installed successfully!"

# Run all tests
test:
	@echo "Running all tests..."
	python -m pytest tests/ -v --alluredir=allure-results

# Run unit tests only
test-unit:
	@echo "Running unit tests..."
	python -m pytest tests/ -v --alluredir=allure-results -m "unit"

# Run integration tests only
test-integration:
	@echo "Running integration tests..."
	python -m pytest tests/ -v --alluredir=allure-results -m "integration"

# Run YAML suite tests
test-yaml:
	@echo "Running YAML suite tests..."
	@echo "Using test suite: $(SUITE)"
	YAML_SUITE=$(SUITE) python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite"

# Run all tests with report generation
test-all: test generate-report
	@echo "All tests completed with report generation!"

# Run tests and start allure server
test-and-serve: test-yaml generate-report
	@echo "Tests completed! Starting allure server..."
	allure serve allure-results

# Clean test results and reports
clean-results:
	@echo "Cleaning test results and reports..."
	@if [ -d "allure-results" ]; then rm -rf allure-results; fi
	@if [ -d "allure-report" ]; then rm -rf allure-report; fi
	@if [ -d ".pytest_cache" ]; then rm -rf .pytest_cache; fi
	@if [ -d "reports" ]; then find reports -name "*.html" -delete; find reports -name "*.md" -delete; fi
	@echo "Cleanup completed!"

# Generate allure HTML report
generate-report:
	@echo "Generating allure HTML report..."
	@if [ ! -d "allure-results" ]; then \
		echo "No allure results found. Run tests first."; \
		exit 1; \
	fi
	allure generate allure-results -o allure-report --clean
	@echo "Report generated: allure-report/index.html"

# Serve allure report (assumes allure is always running)
serve-report:
	@echo "Starting allure server..."
	allure serve allure-results

# List available YAML test suites
list-suites:
	@echo "Listing available YAML test suites..."
	@find test_suites -name "*.yaml" -type f | sort

# Development targets
dev-setup: install
	@echo "Setting up development environment..."
	@echo "Creating allure-results directory..."
	@mkdir -p allure-results
	@echo "Development setup completed!"

# Quick test with default suite
quick-test:
	@echo "Running quick test with default suite..."
	YAML_SUITE=$(SUITE) python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite"

# Test with specific browser
test-chrome:
	make test-yaml BROWSER=chrome

test-firefox:
	make test-yaml BROWSER=firefox

test-edge:
	make test-yaml BROWSER=edge

# Parallel testing
test-parallel:
	@echo "Running tests in parallel..."
	YAML_SUITE=$(SUITE) python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite" -n 2

# CI/CD friendly targets
ci-test:
	@echo "Running CI tests..."
	python -m pytest tests/ -v --alluredir=allure-results --tb=short --strict-markers
	make generate-report

ci-test-yaml:
	@echo "Running CI YAML tests..."
	YAML_SUITE=$(SUITE) python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite" --tb=short --strict-markers
	make generate-report