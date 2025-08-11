# Test Execution Guide

This document provides comprehensive instructions for running tests and generating Allure reports in the BrowserTest AI framework.

## Quick Start

### For Unix/Linux/Git Bash Users
```bash
# Make the script executable (first time only)
chmod +x run_tests.sh

# Run YAML tests with default suite
./run_tests.sh test-yaml

# Run tests and automatically serve Allure report
./run_tests.sh test-and-serve
```

### For Windows Command Prompt Users
```cmd
# Run YAML tests with default suite
run_tests.bat test-yaml

# Run tests and automatically serve Allure report
run_tests.bat test-and-serve
```

### Direct pytest Commands
```bash
# Run YAML tests directly
python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite"

# Generate Allure report
allure generate allure-results -o allure-report --clean

# Serve Allure report
allure serve allure-results
```

## Available Commands

### Test Execution
- `test` - Run all tests
- `test-unit` - Run unit tests only
- `test-integration` - Run integration tests only
- `test-yaml` - Run YAML suite tests
- `test-all` - Run all tests with report generation
- `quick-test` - Run quick test with default suite
- `test-parallel` - Run tests in parallel

### Report Management
- `generate-report` - Generate Allure HTML report
- `serve-report` - Start Allure server
- `test-and-serve` - Run tests and start Allure server

### Utilities
- `install` - Install dependencies
- `clean-results` - Clean test results and reports
- `list-suites` - List available YAML test suites
- `ci-test` - Run CI tests with report
- `ci-test-yaml` - Run CI YAML tests with report

## Environment Variables

Customize test execution using environment variables:

```bash
# Specify a different test suite
SUITE=test_suites/dev/example.yaml ./run_tests.sh test-yaml

# Change browser (chrome, firefox, safari, edge)
BROWSER=firefox ./run_tests.sh test-yaml

# Run in non-headless mode
HEADLESS=false ./run_tests.sh test-yaml

# Filter tests by markers
MARKERS="smoke" ./run_tests.sh test

# Set parallel workers
PARALLEL=4 ./run_tests.sh test-parallel
```

## Test Suite Organization

The framework uses a hierarchical Allure suite structure:

- **Parent Suite**: Environment (e.g., "Production Environment")
- **Suite**: Test suite name (e.g., "MRGB Blog Production Test Suite")
- **Sub Suite**: Individual test case name
- **Epic/Feature/Story**: Additional categorization labels

## Examples

### Basic Test Execution
```bash
# Run default production test suite
./run_tests.sh test-yaml

# Run with custom suite
SUITE=test_suites/staging/api_tests.yaml ./run_tests.sh test-yaml
```

### Parallel Testing
```bash
# Run tests in parallel with 4 workers
PARALLEL=4 ./run_tests.sh test-parallel

# Run integration tests in parallel
PARALLEL=2 ./run_tests.sh test-integration
```

### Report Generation
```bash
# Generate report after running tests
./run_tests.sh test-yaml
./run_tests.sh generate-report

# Run tests and automatically serve report
./run_tests.sh test-and-serve
```

### CI/CD Integration
```bash
# Run CI-friendly tests with strict markers
./run_tests.sh ci-test-yaml

# Clean previous results before CI run
./run_tests.sh clean-results
./run_tests.sh ci-test
```

## Troubleshooting

### Common Issues

1. **Allure command not found**
   ```bash
   # Install Allure
   npm install -g allure-commandline
   # or
   pip install allure-pytest
   ```

2. **Permission denied on run_tests.sh**
   ```bash
   chmod +x run_tests.sh
   ```

3. **Tests not found**
   - Verify test suite path exists
   - Check YAML_SUITE environment variable
   - Use `./run_tests.sh list-suites` to see available suites

4. **Browser issues**
   - Ensure browser drivers are installed
   - Try different browser: `BROWSER=firefox ./run_tests.sh test-yaml`
   - Run in non-headless mode: `HEADLESS=false ./run_tests.sh test-yaml`

### Debug Mode
```bash
# Run with verbose output
python -m pytest tests/test_yaml_suites.py -v -s --alluredir=allure-results

# Run single test case
python -m pytest tests/test_yaml_suites.py::test_yaml_test_case -v -s
```

## Integration with IDEs

### VS Code
Add to `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run YAML Tests",
            "type": "shell",
            "command": "./run_tests.sh test-yaml",
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
```

### PyCharm
1. Go to Run/Debug Configurations
2. Add new Python configuration
3. Set script path to `pytest`
4. Set parameters: `tests/test_yaml_suites.py -v --alluredir=allure-results -m yaml_suite`

## Performance Optimization

### Parallel Execution
- Use `test-parallel` for faster execution
- Adjust `PARALLEL` variable based on system resources
- Monitor memory usage with multiple browser instances

### Resource Management
- Clean results regularly: `./run_tests.sh clean-results`
- Use headless mode for CI: `HEADLESS=true`
- Limit test scope with markers: `MARKERS="smoke"`

## Continuous Integration

For CI/CD pipelines, use the CI-specific commands:

```yaml
# GitHub Actions example
- name: Run Tests
  run: ./run_tests.sh ci-test-yaml
  
- name: Upload Allure Results
  uses: actions/upload-artifact@v3
  with:
    name: allure-results
    path: allure-results/
```

The CI commands include:
- Strict marker validation
- Short traceback format
- Automatic report generation
- Exit on first failure (fail-fast)