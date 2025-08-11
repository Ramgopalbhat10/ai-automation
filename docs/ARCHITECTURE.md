# BrowserTest AI - Architecture Documentation

## Overview

BrowserTest AI is a modular, intelligent browser automation testing framework that combines the power of Large Language Models (LLMs) with the `browser-use` library to enable natural language-driven browser testing. The framework allows users to write tests using simple prompts instead of complex action sequences.

## Core Philosophy

- **Natural Language First**: Tests are written as human-readable prompts
- **Modular Design**: Clear separation of concerns across modules
- **LLM-Powered**: Leverages AI for intelligent browser interactions
- **Configuration-Driven**: YAML-based test definitions
- **Multi-Provider Support**: Pluggable LLM providers
- **Scalable Execution**: Parallel test execution capabilities

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    BrowserTest AI Framework                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Scripts   │    │    Docs     │    │ Test Suites │          │
│  │             │    │             │    │             │          │
│  │ • demo.py   │    │ • tasks.md  │    │ • examples/ │          │
│  │ • setup.py  │    │ • ARCH.md   │    │ • staging/  │          │
│  │ • test_*.py │    │ • README.md │    │ • prod/     │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                        Core Modules                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────────┐        │
│  │   Config    │    │Test Engine  │    │LLM Integration│        │
│  │             │    │             │    │               │        │
│  │ • Config    │◄───┤ • TestEngine│◄───┤ • LLMProvider │        │
│  │ • YAMLLoader│    │ • TestRunner│    │ • GoogleProv  │        │
│  │ • Schema    │    │ • Results   │    │ • OpenAIProv  │        │
│  └─────────────┘    └─────────────┘    └───────────────┘        │
│                                                                 │
│  ┌─────────────┐                                                │
│  │Browser Mgr  │                                                │
│  │             │                                                │
│  │ • BrowserMgr│◄───────────────────────────────────────────────┤
│  │ • Sessions  │                                                │
│  └─────────────┘                                                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                   Testing Infrastructure                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Pytest    │    │   Allure    │    │Cross-Platform│          │
│  │  Framework  │    │  Reporting  │    │   Scripts   │          │
│  │ • Fixtures  │    │ • Reports   │    │ • run_tests │          │
│  │ • Plugins   │    │ • History   │    │ • Makefile  │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    External Dependencies                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │browser-use  │    │  Playwright │    │ LLM APIs    │          │
│  │             │    │             │    │             │          │
│  │ • Agent     │    │ • Browsers  │    │ • Google    │          │
│  │ • Vision    │    │ • Automation│    │ • OpenAI    │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Module Breakdown

### 1. Configuration Module (`config/`)

**Purpose**: Centralized configuration management and YAML processing

**Components**:
- `Config`: Main configuration class that loads environment variables and settings
- `YAMLLoader`: Loads and validates YAML test suite files
- `yaml_schema.py`: Defines data structures (TestSuite, TestCase, BrowserConfig)

**Key Responsibilities**:
- Environment variable management
- YAML file parsing and validation
- Configuration inheritance and defaults
- Schema validation

### 2. Test Engine Module (`test_engine/`)

**Purpose**: Core test execution orchestration

**Components**:
- `TestEngine`: Main orchestrator for test suite execution
- `TestRunner`: Individual test case executor
- `ResultCollector`: Collects and manages test results

**Key Responsibilities**:
- Test suite orchestration
- Parallel execution management
- Result aggregation
- Error handling and retries

### 3. LLM Integration Module (`llm_integration/`)

**Purpose**: LLM provider abstraction and browser-use integration

**Components**:
- `LLMProvider`: Abstract base class for LLM providers
- `GoogleProvider`: Google Gemini integration
- `OpenAIProvider`: OpenAI GPT integration
- `BrowserUseIntegration`: Bridge between LLMs and browser-use

**Key Responsibilities**:
- LLM provider abstraction
- API credential management
- browser-use Agent creation
- Vision capability detection

### 4. Browser Manager Module (`browser_manager/`)

**Purpose**: Browser configuration and session management

**Components**:
- `BrowserManager`: Browser configuration and session tracking

**Key Responsibilities**:
- Browser configuration management
- Session lifecycle management
- Multi-browser support

## Data Flow Architecture

```
┌─────────────┐
│ YAML Test   │
│ Suite File  │
└──────┬──────┘
       │
       ▼
┌─────────────┐    ┌─────────────┐
│ YAMLLoader  │───►│ TestSuite   │
│ • Parse     │    │ Object      │
│ • Validate  │    │             │
└─────────────┘    └──────┬──────┘
                          │
                          ▼
┌─────────────┐    ┌─────────────┐
│ TestEngine  │◄───┤ Config      │
│ • Orchestr. │    │ • LLM Keys  │
│ • Parallel  │    │ • Browser   │
└──────┬──────┘    └─────────────┘
       │
       ▼
┌─────────────┐    ┌─────────────┐
│ TestRunner  │───►│ LLMProvider │
│ • Execute   │    │ • Google    │
│ • Monitor   │    │ • OpenAI    │
└──────┬──────┘    └──────┬──────┘
       │                  │
       ▼                  ▼
┌─────────────┐    ┌─────────────┐
│BrowserUse   │◄───┤ Agent       │
│Integration  │    │ • LLM       │
│             │    │ • Vision    │
└──────┬──────┘    └─────────────┘
       │
       ▼
┌─────────────┐    ┌─────────────┐
│ Browser     │───►│ Web Page    │
│ Automation  │    │ Interaction │
│             │    │             │
└──────┬──────┘    └─────────────┘
       │
       ▼
┌─────────────┐
│ Test Result │
│ Collection  │
│             │
└─────────────┘
```

## Execution Flow

### 1. Initialization Phase

```
1. Load Configuration
   ├── Environment variables (.env)
   ├── Default settings
   └── Command-line overrides

2. Initialize Components
   ├── LLM Provider (Google/OpenAI)
   ├── Browser Manager
   ├── Test Engine
   └── Result Collector

3. Validate Setup
   ├── API credentials
   ├── Browser availability
   └── Test suite files
```

### 2. Test Suite Loading

```
1. Parse YAML File
   ├── Load test suite configuration
   ├── Validate schema
   └── Create TestSuite object

2. Process Test Cases
   ├── Extract individual tests
   ├── Apply default configurations
   └── Resolve variables

3. Setup Execution Plan
   ├── Determine execution order
   ├── Configure parallelism
   └── Setup retry policies
```

### 3. Test Execution

```
1. For Each Test Case:
   ├── Create browser-use Agent
   ├── Configure LLM and browser settings
   ├── Execute natural language prompt
   ├── Monitor execution
   ├── Capture results and screenshots
   └── Handle errors and retries

2. Parallel Execution (if enabled):
   ├── Create worker pool
   ├── Distribute tests across workers
   ├── Manage browser sessions
   └── Aggregate results

3. Result Collection:
   ├── Collect individual test results
   ├── Generate execution summary
   ├── Create reports (HTML/JSON)
   └── Cleanup resources
```

## Component Interactions

### Primary Interaction Flow

```
User Script
    │
    ▼
TestEngine.execute_test_suite()
    │
    ├─► Config.get() ──────────────► Environment Variables
    │
    ├─► YAMLLoader.load_test_suite() ► YAML File
    │
    ├─► LLMProvider.create_provider() ► API Credentials
    │
    └─► TestRunner.run_test()
            │
            ├─► BrowserUseIntegration.create_agent()
            │       │
            │       ├─► LLMProvider.get_llm()
            │       └─► BrowserManager.get_browser_config()
            │
            ├─► Agent.run() ──────────► Browser Automation
            │
            └─► ResultCollector.add_result() ► Test Results
```

### Configuration Flow

```
Environment Variables (.env)
    │
    ▼
Config.__init__()
    │
    ├─► LLM Configuration
    │   ├─► Provider type (google/openai)
    │   ├─► API keys
    │   └─► Model selection
    │
    ├─► Browser Configuration
    │   ├─► Headless mode
    │   ├─► Viewport size
    │   └─► Timeout settings
    │
    └─► Execution Configuration
        ├─► Parallel workers
        ├─► Retry policies
        └─► Output directories
```

## Key Design Patterns

### 1. Factory Pattern
- **LLMProvider.create_provider()**: Creates appropriate LLM provider instances
- **Agent creation**: Dynamic agent instantiation based on configuration

### 2. Strategy Pattern
- **LLMProvider**: Pluggable LLM implementations
- **Browser configurations**: Different browser strategies

### 3. Observer Pattern
- **ResultCollector**: Collects results from multiple test runners
- **Progress monitoring**: Real-time execution updates

### 4. Template Method Pattern
- **TestRunner.run_test()**: Standardized test execution flow
- **Result generation**: Consistent reporting structure

## Configuration System

### Environment Variables

```bash
# LLM Configuration
LLM_PROVIDER=google              # google, openai, groq
GOOGLE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
LLM_MODEL=gemini-2.0-flash-exp

# Browser Configuration
BROWSER_HEADLESS=false
BROWSER_TYPE=chromium
BROWSER_TIMEOUT=30000
BROWSER_POOL_SIZE=3

# Execution Configuration
PARALLEL_WORKERS=2
MAX_RETRIES=3
RETRY_DELAY=5

# Reporting Configuration
OUTPUT_DIR=reports
REPORT_FORMAT=html,json
```

### YAML Test Suite Structure

```yaml
name: "Test Suite Name"
description: "Test suite description"

# Execution settings
parallel: false
max_workers: 2
fail_fast: false

# Default configurations
default_browser:
  type: "chromium"
  headless: false
  viewport:
    width: 1920
    height: 1080
  timeout: 30000

default_llm_provider: "google"
base_url: "https://example.com"

# Test cases
tests:
  - name: "Test Name"
    description: "Test description"
    prompt: "Natural language instruction"
    success_criteria: "Expected outcome"
    url: "https://target-url.com"
    timeout: 30
    retry_count: 2
    tags: ["category1", "category2"]

# Global variables
variables:
  key: "value"

# Reporting
report_format: ["html", "json"]
```

## Running the Application

### Prerequisites

1. **Python Environment**:
   ```bash
   python >= 3.8
   pip install -r requirements.txt
   ```

2. **API Keys**:
   - Google Gemini API key (recommended)
   - OpenAI API key (optional)
   - Groq API key (optional)

3. **Environment Setup**:
   ```bash
   # Create .env file
   echo "GOOGLE_API_KEY=your_key_here" > .env
   echo "LLM_PROVIDER=google" >> .env
   ```

4. **Testing Infrastructure**:
   - **Pytest Framework**: Modern testing framework with fixtures and plugins
   - **Allure Reporting**: Advanced test reporting with rich visualizations
   - **Cross-Platform Scripts**: Unix/Linux/Windows compatible test execution
   - **Makefile Support**: Simplified command execution for development workflows

### Execution Methods

#### 1. Direct Script Execution

```bash
# Run demo (no API key required)
python scripts/demo.py

# Run example test
python scripts/example_windsurf_test.py

# Run website tester
python scripts/website_tester.py

# Run Amazon E2E test
python scripts/test_amazon_e2e.py
```

#### 2. Universal CLI (Recommended)

```bash
python main.py run test_suites/examples/example_test_suite.yaml
python main.py validate test_suites/examples/example_test_suite.yaml
```

#### 3. Pytest Integration

```bash
# Run all tests with Allure reporting
pytest --alluredir=reports/allure-results

# Run specific test suites
pytest tests/test_yaml_suites.py::test_example_suite

# Cross-platform execution scripts
./run_tests.sh all-tests        # Unix/Linux/Git Bash
run_tests.bat all-tests         # Windows
```

#### 4. Makefile Commands

```bash
make install     # Install dependencies
make test        # Run all tests
make test-unit   # Run unit tests only
make clean       # Clean reports
make report      # Generate and serve Allure report
```

#### 5. Test Engine Usage

```python
import asyncio
from config import Config
from test_engine.test_engine import TestEngine
from config.yaml_loader import YAMLLoader

async def run_tests():
    # Initialize
    config = Config()
    test_engine = TestEngine(config)
    
    # Load test suite
    test_suite = YAMLLoader.load_test_suite(
        "test_suites/examples/example_test_suite.yaml"
    )
    
    # Execute
    results = await test_engine.execute_test_suite(test_suite)
    print(f"Tests completed: {results}")

asyncio.run(run_tests())
```

#### 3. Configuration Validation

```bash
# Validate refactoring
python scripts/validate_refactoring.py

# Test core engine
python scripts/test_core_engine.py

# Test YAML configuration
python scripts/test_yaml_config.py
```

### Development Workflow

1. **Setup Development Environment**:
   ```bash
   git clone <repository>
   cd ai-automation
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Validation**:
   ```bash
   python scripts/validate_refactoring.py
   ```

4. **Create Test Suites**:
   - Add YAML files to `test_suites/examples/`
   - Follow the schema in existing examples
   - Use natural language prompts

5. **Execute Tests**:
   ```bash
   python scripts/test_core_engine.py
   ```

## Error Handling and Debugging

### Common Issues

1. **API Key Issues**:
   - Verify API keys in environment variables
   - Check API quotas and limits
   - Validate provider configuration

2. **Browser Issues**:
   - Ensure Playwright browsers are installed
   - Check headless mode settings
   - Verify browser permissions

3. **YAML Validation**:
   - Use schema validation tools
   - Check indentation and syntax
   - Validate required fields

### Debugging Tools

1. **Validation Scripts**:
   ```bash
   python scripts/validate_refactoring.py
   python scripts/test_core_engine.py
   ```

2. **Configuration Testing**:
   ```bash
   python scripts/test_yaml_config.py
   ```

3. **Demo Mode**:
   ```bash
   python scripts/demo.py
   ```

## Extension Points

### Adding New LLM Providers

1. Create new provider class inheriting from `LLMProvider`
2. Implement required abstract methods
3. Add to factory method in `LLMProvider.create_provider()`
4. Update configuration options

### Adding New Browser Types

1. Extend `BrowserType` enum in `yaml_schema.py`
2. Update `BrowserManager` configuration
3. Add browser-specific settings

### Custom Test Actions

1. Extend `TestCase` with custom fields
2. Update YAML schema validation
3. Implement custom execution logic in `TestRunner`

### Custom Reporting

1. Extend `ResultCollector` with new formats
2. Add report generation methods
3. Update configuration options

## Performance Considerations

### Parallel Execution
- Configure `max_workers` based on system resources
- Monitor browser memory usage
- Use browser session pooling for efficiency

### Resource Management
- Implement proper cleanup in test runners
- Monitor API rate limits
- Use connection pooling for LLM providers

### Optimization Tips
- Use headless mode for faster execution
- Implement smart retry strategies
- Cache common browser configurations
- Optimize YAML loading for large test suites

## Security Considerations

### API Key Management
- Store keys in environment variables
- Never commit keys to version control
- Use secure key rotation practices
- Implement key validation

### Browser Security
- Use isolated browser sessions
- Implement proper cleanup
- Avoid storing sensitive data in browser
- Use secure download directories

### Test Data Security
- Sanitize test inputs
- Avoid hardcoded credentials
- Use secure test data management
- Implement data cleanup procedures

## Future Enhancements

### Planned Features
- CLI interface for test execution
- Advanced reporting with charts
- Test result trending
- Integration with CI/CD pipelines
- Mobile browser testing
- API testing capabilities

### Architecture Improvements
- Plugin system for extensions
- Distributed test execution
- Real-time test monitoring
- Advanced error recovery
- Performance profiling

---

*This documentation provides a comprehensive overview of the BrowserTest AI architecture. For specific implementation details, refer to the individual module documentation and source code.*