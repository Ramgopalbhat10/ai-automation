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

# Preserve history from previous report
preserve-history:
	@echo "Preserving test history..."
	@if [ -d "allure-report/history" ]; then \
		mkdir -p allure-results; \
		cp -r allure-report/history allure-results/; \
		echo "History preserved from previous report"; \
	else \
		echo "No previous history found"; \
	fi

# Clean results but preserve history
clean-preserve-history:
	@echo "Cleaning test results while preserving history..."
	@if [ -d "allure-report/history" ]; then \
		mkdir -p allure-results; \
		cp -r allure-report/history allure-results/; \
	fi
	@if [ -d "allure-results" ]; then \
		find allure-results -type f ! -path "allure-results/history/*" -delete 2>/dev/null || true; \
		find allure-results -type d -empty ! -path "allure-results/history*" -delete 2>/dev/null || true; \
	fi
	@if [ -d "allure-report" ]; then rm -rf allure-report; fi
	@if [ -d ".pytest_cache" ]; then rm -rf .pytest_cache; fi
	@if [ -d "reports" ]; then find reports -name "*.html" -delete; find reports -name "*.md" -delete; fi
	@echo "Cleanup completed with history preserved!"

# Generate allure HTML report
generate-report:
	@echo "Generating allure HTML report..."
	@if [ ! -d "allure-results" ]; then \
		echo "No allure results found. Run tests first."; \
		exit 1; \
	fi
	allure generate allure-results -o allure-report --clean
	@echo "Report generated: allure-report/index.html"

# Generate report with history preservation
generate-report-with-history:
	@echo "Generating allure HTML report with history..."
	@if [ ! -d "allure-results" ]; then \
		echo "No allure results found. Run tests first."; \
		exit 1; \
	fi
	@if [ -d "allure-report/history" ] && [ ! -d "allure-results/history" ]; then \
		echo "Copying history from previous report..."; \
		cp -r allure-report/history allure-results/; \
	fi
	allure generate allure-results -o allure-report
	@echo "Report with history generated: allure-report/index.html"

# Generate timestamped report for archival
generate-timestamped-report:
	@echo "Generating timestamped report..."
	@if [ ! -d "allure-results" ]; then \
		echo "No allure results found. Run tests first."; \
		exit 1; \
	fi
	$(eval TIMESTAMP := $(shell date +"%Y%m%d_%H%M%S"))
	@mkdir -p allure-reports-archive
	allure generate allure-results -o allure-reports-archive/allure-report-$(TIMESTAMP)
	@echo "Timestamped report generated: allure-reports-archive/allure-report-$(TIMESTAMP)/index.html"

# Archive current results with timestamp
archive-results:
	@echo "ℹ Archiving current test results..."
	@timestamp=$$(date +"%Y-%m-%d-%H-%M"); \
	mkdir -p archived-results archived-reports; \
	if [ -d "allure-results" ]; then \
		cp -r allure-results "archived-results/results-$$timestamp"; \
		echo "✓ Results archived to: archived-results/results-$$timestamp"; \
	fi; \
	if [ -d "allure-report" ]; then \
		cp -r allure-report "archived-reports/report-$$timestamp"; \
		echo "✓ Report archived to: archived-reports/report-$$timestamp"; \
	fi

# Complete automated workflow with history management
test-with-history:
	@echo "ℹ Starting automated test workflow with history management..."
	@echo "ℹ Test type: yaml (default)"
	@echo "ℹ Step 1/6: Preserving test history..."
	@$(MAKE) preserve-history
	@echo "ℹ Step 2/6: Cleaning old results while preserving history..."
	@$(MAKE) clean-preserve-history
	@echo "ℹ Step 3/6: Running tests..."
	@$(MAKE) test-yaml
	@echo "ℹ Step 4/6: Generating report with history..."
	@$(MAKE) generate-report-with-history
	@echo "ℹ Step 5/6: Creating timestamped archive..."
	@$(MAKE) generate-timestamped-report
	@echo "ℹ Step 6/6: Starting Allure server..."
	@echo "✓ 🎉 Automated workflow completed successfully!"
	@echo "ℹ Report available at: allure-report/index.html"
	@echo "ℹ Starting server for immediate viewing..."
	@$(MAKE) serve-report

test-with-history-parallel:
	@echo "ℹ Starting automated test workflow with history management (parallel)..."
	@echo "ℹ Test type: parallel"
	@echo "ℹ Step 1/6: Preserving test history..."
	@$(MAKE) preserve-history
	@echo "ℹ Step 2/6: Cleaning old results while preserving history..."
	@$(MAKE) clean-preserve-history
	@echo "ℹ Step 3/6: Running tests in parallel..."
	@$(MAKE) test-parallel
	@echo "ℹ Step 4/6: Generating report with history..."
	@$(MAKE) generate-report-with-history
	@echo "ℹ Step 5/6: Creating timestamped archive..."
	@$(MAKE) generate-timestamped-report
	@echo "ℹ Step 6/6: Starting Allure server..."
	@echo "✓ 🎉 Automated workflow completed successfully!"
	@echo "ℹ Report available at: allure-report/index.html"
	@echo "ℹ Starting server for immediate viewing..."
	@$(MAKE) serve-report

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