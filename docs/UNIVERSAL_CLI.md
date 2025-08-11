# Universal CLI Architecture

## Problem Statement

Previously, the framework required creating separate Python scripts for each test suite (like `run_mrgb_tests.py`, `demo_multi_tab.py`), which doesn't scale well when you have many test suites. Each test suite would need its own runner script, leading to:

- **Code Duplication**: Similar test execution logic repeated across scripts
- **Maintenance Overhead**: Updates needed in multiple places
- **Poor Scalability**: One script per test suite doesn't scale
- **Inconsistent Interfaces**: Different scripts might have different command-line options

## Solution: Universal CLI

The new `main.py` provides a **universal CLI** that can execute any YAML test suite without requiring separate Python scripts. The core `TestEngine` reads the YAML configuration and handles all test types automatically.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   main.py       │    │   TestEngine     │    │   YAML Loader   │
│   (Universal    │───▶│   (Core Engine)  │───▶│   (Config)      │
│    CLI)         │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Commands  │    │   Test Execution │    │   YAML Files    │
│   • run         │    │   • Sequential   │    │   • Any .yaml   │
│   • list        │    │   • Parallel     │    │   • Any .yml    │
│   • validate    │    │   • Multi-tab    │    │   • Validated   │
│   • template    │    │   • Multi-LLM    │    │   • Structured  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Key Components

### 1. Universal Entry Point (`main.py`)

- **Single CLI Interface**: One command-line interface for all test suites
- **Configuration Overrides**: Command-line options can override YAML settings
- **Auto-Discovery**: Lists all available test suites automatically
- **Validation**: Built-in YAML validation before execution
- **Template Generation**: Creates new test suite templates

### 2. Core Test Engine (`test_engine/test_engine.py`)

- **YAML-Driven**: Reads configuration from any YAML file
- **Multi-Execution Modes**: Supports sequential, parallel, and multi-tab execution
- **LLM Integration**: Works with any configured LLM provider
- **Browser Management**: Handles browser lifecycle automatically
- **Result Collection**: Standardized result collection and reporting

### 3. YAML Configuration System

- **Schema Validation**: Ensures YAML files are properly structured
- **Flexible Configuration**: Supports all test types and configurations
- **Environment Variables**: Dynamic configuration through environment variables
- **Default Inheritance**: Sensible defaults with override capabilities

## Usage Examples

### Running Any Test Suite

```bash
# Run the MRGB blog test suite
python main.py run test_suites/production/mrgb_blog_test_suite.yaml

# Run Amazon test suite with parallel execution
python main.py run test_suites/examples/amazon_test_suite.yaml --parallel --workers 3

# Run with different browser and LLM
python main.py run test_suites/examples/example_test_suite.yaml --browser firefox --llm-provider openai
```

### Managing Test Suites

```bash
# List all available test suites
python main.py list

# Validate a test suite before running
python main.py validate test_suites/production/mrgb_blog_test_suite.yaml

# Create a new test suite from template
python main.py template --output my_new_test_suite.yaml
```

## Benefits

### 1. **Scalability**
- ✅ **One CLI for All**: Single interface handles unlimited test suites
- ✅ **No Script Proliferation**: No need to create separate runner scripts
- ✅ **Consistent Interface**: Same commands and options for all test suites

### 2. **Maintainability**
- ✅ **Single Source of Truth**: All execution logic in one place
- ✅ **Easy Updates**: Changes apply to all test suites automatically
- ✅ **Reduced Code Duplication**: Common functionality shared across all tests

### 3. **Flexibility**
- ✅ **Configuration Overrides**: Command-line options override YAML settings
- ✅ **Multi-LLM Support**: Switch between LLM providers easily
- ✅ **Multi-Browser Support**: Test across different browsers
- ✅ **Execution Modes**: Sequential, parallel, or multi-tab execution

### 4. **Developer Experience**
- ✅ **Auto-Discovery**: Automatically finds and lists test suites
- ✅ **Validation**: Built-in YAML validation with helpful error messages
- ✅ **Template Generation**: Quick start for new test suites
- ✅ **Comprehensive Help**: Built-in help and examples

## Migration from Custom Scripts

If you have existing custom scripts like `run_mrgb_tests.py`, you can now replace them with the universal CLI:

### Before (Custom Script)
```bash
python scripts/run_mrgb_tests.py
```

### After (Universal CLI)
```bash
python main.py run test_suites/production/mrgb_blog_test_suite.yaml
```

### Benefits of Migration
- **Consistency**: Same interface for all test suites
- **Maintenance**: No need to maintain separate scripts
- **Features**: Access to all CLI features (validation, templates, etc.)
- **Flexibility**: Easy configuration overrides

## Advanced Features

### Configuration Overrides

The CLI allows overriding YAML configuration at runtime:

```bash
# Override parallel execution
python main.py run test_suite.yaml --parallel --workers 5

# Override browser settings
python main.py run test_suite.yaml --browser chrome --headless

# Override LLM provider
python main.py run test_suite.yaml --llm-provider groq
```

### Multi-Tab Support

The universal CLI automatically handles multi-tab execution based on YAML configuration:

```yaml
# In your YAML file
parallel: true
max_workers: 3
default_browser:
  type: "chromium"
  keep_alive: true  # Enables multi-tab support
```

### Pytest Integration
The Universal CLI now integrates seamlessly with pytest for enhanced testing capabilities:

```bash
# Run tests through pytest with Allure reporting
pytest --alluredir=reports/allure-results

# Run specific test categories
pytest tests/test_yaml_suites.py -k "integration"
pytest tests/test_browser.py -k "chrome"

# Cross-platform execution scripts
./run_tests.sh all-tests        # Unix/Linux/Git Bash
run_tests.bat all-tests         # Windows

# Available test commands (14 total)
./run_tests.sh list-commands    # See all available commands
```

### Makefile Integration
Simplified development workflow with make commands:

```bash
make install     # Install dependencies
make test        # Run all tests with Allure
make test-unit   # Run unit tests only
make test-integration  # Run integration tests
make clean       # Clean reports and cache
make report      # Generate and serve Allure report
make list-suites # List available test suites
```

### Environment Integration

The CLI respects environment variables and can be easily integrated into CI/CD pipelines:

```bash
# Set environment variables
export GOOGLE_API_KEY="your-api-key"
export BROWSER_HEADLESS="true"

# Run tests
python main.py run test_suites/production/mrgb_blog_test_suite.yaml
```

## Future Enhancements

### Planned Features
- **Batch Execution**: Run multiple test suites in sequence
- **Report Aggregation**: Combine results from multiple test suites
- **Watch Mode**: Automatically re-run tests when YAML files change
- **Remote Execution**: Run test suites on remote machines
- **Plugin System**: Extend functionality with custom plugins

### Integration Possibilities
- **CI/CD Integration**: Easy integration with GitHub Actions, Jenkins, etc.
- **Docker Support**: Containerized test execution
- **Cloud Execution**: Run tests on cloud platforms
- **Monitoring Integration**: Send results to monitoring systems

## Conclusion

The Universal CLI architecture solves the scalability problem by providing a single, powerful interface that can handle any YAML test suite. This approach:

1. **Eliminates the need for separate Python scripts** for each test suite
2. **Provides a consistent, feature-rich interface** for all test execution
3. **Scales effortlessly** as you add more test suites
4. **Reduces maintenance overhead** by centralizing execution logic
5. **Improves developer experience** with built-in validation, templates, and help

The core `TestEngine` does all the heavy lifting based on YAML configuration, making the framework truly configuration-driven and scalable.