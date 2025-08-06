# BrowserTest AI

A modular, intelligent browser automation testing framework that uses the `browser-use` library with LLM integration for natural language test creation and execution.

## 🚀 Features

- **Natural Language Testing**: Write tests using simple prompts instead of complex action sequences
- **Multi-LLM Support**: Configurable LLM providers (Google Gemini, OpenAI, etc.)
- **Cross-Browser Testing**: Support for Chrome, Firefox, Safari, Edge
- **Parallel Execution**: Concurrent test execution with browser session pooling
- **Environment Management**: Multi-environment support (dev, staging, production)
- **YAML Configuration**: Simple, readable test definitions
- **Comprehensive Reporting**: HTML, JSON, and JUnit report formats

## 📁 Project Structure

```
ai-automation/
├── config/                 # Configuration management
│   ├── yaml_schema.py     # YAML schema definitions
│   ├── yaml_loader.py     # YAML file loader
│   └── test_config.py     # Configuration tests
├── llm_integration/        # LLM provider integrations
├── test_engine/           # Core test execution engine
├── test_suites/           # Test suite definitions
│   ├── examples/          # Example test suites
│   ├── production/        # Production test suites
│   └── staging/           # Staging test suites
├── reports/               # Test execution reports
├── requirements.txt       # Python dependencies
├── setup.py              # Package setup
└── tasks.md              # Development tasks
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-automation
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install the package**:
   ```bash
   pip install -e .
   ```

## 📝 Writing Tests

Tests are defined using simple YAML files with natural language prompts:

```yaml
name: "E-commerce Website Testing"
description: "Test online store functionality"
base_url: "https://demo.opencart.com"

default_browser:
  type: "chrome"
  headless: false
  viewport:
    width: 1920
    height: 1080

variables:
  test_email: "demo@example.com"
  search_term: "laptop"

tests:
  - name: "Homepage Navigation"
    prompt: "Navigate to the homepage and verify it loads correctly with all main navigation elements visible"
    success_criteria: "Page title is correct, navigation menu is visible, and main content loads"
    timeout: 30
    tags: ["smoke", "navigation"]
    
  - name: "Product Search"
    prompt: "Use the search functionality to find laptops and verify search results are displayed correctly"
    success_criteria: "Search results page shows relevant laptop products with images and prices"
    timeout: 45
    tags: ["search", "products"]
```

## 🎯 Key Concepts

### Natural Language Prompts
Instead of defining explicit actions and assertions, you describe what you want to test in natural language:

- **Prompt**: What the test should do
- **Success Criteria**: How to determine if the test passed
- **Variables**: Dynamic values for test data

### Simplified Configuration
The framework focuses on:
- **Prompt-based testing** using LLM intelligence
- **Minimal configuration** with sensible defaults
- **Environment-specific** test execution
- **Flexible browser** and execution settings

## 🔧 Configuration

### Browser Settings
```yaml
default_browser:
  type: "chrome"          # chrome, firefox, webkit, edge
  headless: false         # Run in headless mode
  viewport:
    width: 1920
    height: 1080
  timeout: 30000          # Page load timeout (ms)
```

### Test Execution
```yaml
parallel: false           # Run tests in parallel
max_workers: 2            # Number of parallel workers
fail_fast: false          # Stop on first failure
```

### Environment Variables
```yaml
variables:
  test_user: "${TEST_USER}"     # Environment variable
  base_url: "https://staging.example.com"
  timeout: 60
```

## 🚀 Usage

### Universal CLI - No Separate Scripts Needed!

The framework now includes a **universal CLI** that can run any YAML test suite without requiring separate Python scripts for each test suite. This solves the scalability issue!

### Running Tests
```bash
# Run any test suite directly
python main.py run test_suites/examples/example_test_suite.yaml
python main.py run test_suites/production/mrgb_blog_test_suite.yaml

# Run with configuration overrides
python main.py run test_suites/examples/example_test_suite.yaml --parallel --workers 4
python main.py run test_suites/production/mrgb_blog_test_suite.yaml --browser chrome --headless

# Use different LLM providers
python main.py run test_suites/examples/example_test_suite.yaml --llm-provider openai
python main.py run test_suites/examples/example_test_suite.yaml --llm-provider groq
```

### Managing Test Suites
```bash
# List all available test suites
python main.py list

# Validate YAML syntax and schema
python main.py validate test_suites/examples/example_test_suite.yaml

# Generate template for new test suite
python main.py template --output my_test_suite.yaml
```

### CLI Options
```bash
# Available run options:
--parallel          # Force parallel execution
--sequential        # Force sequential execution  
--workers N         # Number of parallel workers
--llm-provider X    # LLM provider (google, openai, groq)
--browser X         # Browser (chrome, firefox, webkit, edge)
--headless          # Run in headless mode
```

## 🧪 Testing the Framework

Run the configuration tests to ensure everything is working:

```bash
cd config
python test_config.py
```

## 📊 Reports

Test results are generated in multiple formats:
- **HTML**: Interactive web reports
- **JSON**: Machine-readable results
- **JUnit**: CI/CD integration

Reports are saved to the `reports/` directory by default.

## 🔌 LLM Integration

The framework supports multiple LLM providers:
- Google Gemini
- OpenAI GPT
- Anthropic Claude
- Local models via Ollama

Configure your preferred provider in the test suite or environment variables.

## 🤝 Contributing

1. Follow the tasks outlined in `tasks.md`
2. Maintain backward compatibility
3. Add tests for new features
4. Update documentation

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the example test suites in `test_suites/examples/`
2. Review the configuration schema in `config/yaml_schema.py`
3. Run the test validation script: `python config/test_config.py`