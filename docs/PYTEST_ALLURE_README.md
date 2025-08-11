# Pytest & Allure Integration for BrowserTest AI

This document describes the pytest and allure integration for BrowserTest AI, enabling advanced test reporting and better test management while maintaining compatibility with existing YAML-based test suites.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Allure CLI (for report generation)
npm install -g allure-commandline
# OR download from: https://github.com/allure-framework/allure2/releases
```

### 2. Run Tests

```bash
# Run all tests with default configuration
python run_pytest.py

# Run specific YAML test suite
python run_pytest.py --yaml-suite test_suites/production/mrgb_blog_test_suite.yaml

# Run tests and generate allure report
python run_pytest.py --generate-report

# Run tests in headless mode
python run_pytest.py --headless
```

### 3. View Reports

```bash
# Generate and serve allure report
python run_pytest.py --generate-report
allure open allure-report

# OR use the runner script
python run_pytest.py --serve-report
```

## 📁 Project Structure

```
ai-automation/
├── tests/                          # Pytest test files
│   ├── __init__.py
│   ├── conftest.py                 # Pytest configuration and fixtures
│   ├── test_yaml_suites.py         # YAML suite adapter for pytest
│   └── test_integration.py         # Integration tests
├── pytest.ini                      # Pytest configuration
├── allure.properties               # Allure configuration
├── run_pytest.py                   # Test runner script
├── Makefile                        # Convenient make targets
├── allure-results/                 # Test results (auto-generated)
├── allure-report/                  # HTML reports (auto-generated)
└── requirements.txt                # Updated with pytest/allure deps
```

## 🔧 Configuration

### Pytest Configuration (`pytest.ini`)

- **Async Support**: Configured for async test execution
- **Allure Integration**: Automatic result collection
- **Custom Markers**: `browser`, `yaml_suite`, `slow`, `integration`, `unit`
- **Logging**: Comprehensive test logging

### Allure Configuration (`allure.properties`)

- **Results Directory**: `allure-results`
- **Report Customization**: Title, description, environment info
- **Link Patterns**: Issue and TMS integration

## 📊 Allure History Management

Allure provides powerful history tracking capabilities that show test trends, execution history, and performance metrics over time. To enable these features, you need to preserve history data between test runs.

### How History Works

Each time Allure generates a test report, it creates data in the `history` subdirectory within `allure-report/`. This data includes:
- Test execution trends (up to 20 latest reports)
- Performance metrics and duration tracking
- Test status history (passed/failed/skipped)
- Flaky test detection
- Execution statistics and graphs

### History Management Commands

#### Using Shell Scripts (Linux/Mac)

```bash
# 1. Preserve history from previous report (before running new tests)
./run_tests.sh preserve-history

# 2. Clean results but keep history
./run_tests.sh clean-preserve-history

# 3. Run your tests
./run_tests.sh test-yaml

# 4. Generate report with history
./run_tests.sh generate-report-with-history

# 5. Create timestamped archive (optional)
./run_tests.sh generate-timestamped-report

# 6. Archive current results for backup
./run_tests.sh archive-results
```

#### Using Batch Scripts (Windows)

```cmd
REM 1. Preserve history from previous report
run_tests.bat preserve-history

REM 2. Clean results but keep history
run_tests.bat clean-preserve-history

REM 3. Run your tests
run_tests.bat test-yaml

REM 4. Generate report with history
run_tests.bat generate-report-with-history

REM 5. Create timestamped archive (optional)
run_tests.bat generate-timestamped-report

REM 6. Archive current results for backup
run_tests.bat archive-results
```

#### Using Makefile

```bash
# Complete workflow with history
make preserve-history
make clean-preserve-history
make test-yaml
make generate-report-with-history

# Or individual commands
make preserve-history          # Copy history from previous report
make clean-preserve-history    # Clean results but preserve history
make generate-report-with-history  # Generate report with history
make generate-timestamped-report   # Create timestamped report
make archive-results          # Archive current results
```

### Automated Workflow (Recommended)

For the easiest experience, use the automated workflow command that handles everything:

#### Single Command Automation

```bash
# Complete automated workflow with YAML tests (default)
./run_tests.sh test-with-history

# Automated workflow with specific test types
./run_tests.sh test-with-history yaml
./run_tests.sh test-with-history parallel
./run_tests.sh test-with-history all
./run_tests.sh test-with-history unit
./run_tests.sh test-with-history integration
./run_tests.sh test-with-history quick
```

#### Windows

```cmd
REM Complete automated workflow
run_tests.bat test-with-history

REM With specific test types
run_tests.bat test-with-history yaml
run_tests.bat test-with-history parallel
```

#### Makefile

```bash
# Automated workflow with YAML tests
make test-with-history

# Automated workflow with parallel execution
make test-with-history-parallel
```

**What the automated workflow does:**
1. ✅ Preserves history from previous reports
2. ✅ Cleans old results while keeping history
3. ✅ Runs your specified tests
4. ✅ Generates report with history
5. ✅ Creates timestamped archive
6. ✅ Starts Allure server for immediate viewing

### Manual Workflow (Advanced Users)

For fine-grained control, follow this sequence:

1. **Before running new tests**:
   ```bash
   # Preserve history from the last report
   ./run_tests.sh preserve-history
   
   # Clean old results but keep history
   ./run_tests.sh clean-preserve-history
   ```

2. **Run your tests**:
   ```bash
   ./run_tests.sh test-yaml
   # or any other test command
   ```

3. **Generate report with history**:
   ```bash
   ./run_tests.sh generate-report-with-history
   ```

4. **Optional - Create archives**:
   ```bash
   # Create timestamped report for archival
   ./run_tests.sh generate-timestamped-report
   
   # Archive results for backup
   ./run_tests.sh archive-results
   ```

### History Features

Once history is properly configured, you'll see:

- **History Tab**: Shows test execution trends over time
- **Trend Charts**: Visual representation of test stability
- **Duration Tracking**: Performance metrics across runs
- **Flaky Test Detection**: Identifies unstable tests
- **Execution Statistics**: Success rates and patterns

### Directory Structure with History

```
ai-automation/
├── allure-results/             # Current test results
│   ├── history/               # History data (copied from previous report)
│   └── *.json                 # Test result files
├── allure-report/             # Generated HTML report
│   ├── history/               # History data for next run
│   └── index.html             # Report entry point
├── archived-results/          # Archived test results (optional)
│   ├── results-2024-01-15-14-30/
│   └── results-2024-01-14-10-15/
└── archived-reports/          # Timestamped reports (optional)
    ├── report-2024-01-15-14-30/
    └── report-2024-01-14-10-15/
```

### Troubleshooting History

1. **Empty History Tab**:
   - Ensure you run `preserve-history` before new tests
   - Check that `allure-report/history` exists after first report generation
   - Verify history data is copied to `allure-results/history` before running tests

2. **Missing Trends**:
   - History requires multiple test runs to show trends
   - Ensure consistent test names across runs
   - Check that history data isn't being cleared between runs

3. **Performance Issues**:
   - History keeps data for up to 20 reports by default
   - Large history files can slow report generation
   - Use `archive-results` to backup and clean old data if needed

## 🧪 Test Types

### 1. YAML Suite Tests

Dynamically generated from YAML test suite files:

```bash
# Run specific YAML suite
python run_pytest.py --yaml-suite test_suites/production/mrgb_blog_test_suite.yaml

# Run with specific browser
python run_pytest.py --yaml-suite test_suites/production/mrgb_blog_test_suite.yaml --browser firefox

# Filter by markers
python run_pytest.py --markers "yaml_suite and not slow"
```

### 2. Integration Tests

Test framework components:

```bash
# Run integration tests only
python run_pytest.py --markers "integration"

# Run unit tests only
python run_pytest.py --markers "unit"
```

### 3. Browser Tests

Browser automation tests:

```bash
# Run browser tests
python run_pytest.py --markers "browser"

# Run in headless mode
python run_pytest.py --markers "browser" --headless
```

## 📊 Allure Reporting Features

### Test Execution Details
- **Step-by-step execution**: Each test action as allure step
- **Screenshots**: Automatic screenshot attachment
- **Logs**: Test output and error logs
- **Timing**: Detailed execution timing

### Test Organization
- **Features**: Grouped by functionality
- **Stories**: Individual test scenarios
- **Tags**: Custom test categorization
- **Severity**: Test importance levels

### Environment Information
- **Browser**: Chrome, Firefox, Safari, Edge
- **Platform**: Operating system details
- **Framework**: pytest + browser-use
- **Project**: BrowserTest AI version info

## 🛠 Advanced Usage

### Custom Test Execution

```bash
# Parallel execution (requires pytest-xdist)
python run_pytest.py --parallel 4

# Custom pytest arguments
python run_pytest.py --pytest-args "--maxfail=1 --tb=line"

# Environment variable
YAML_SUITE=test_suites/staging/test_suite.yaml python run_pytest.py
```

### Using Makefile

```bash
# Install dependencies
make install

# Run all tests
make test

# Run YAML suite with custom browser
make test-yaml BROWSER=firefox SUITE=test_suites/production/mrgb_blog_test_suite.yaml

# Run tests in headless mode
make test-all HEADLESS=true

# Clean results
make clean-results

# List available test suites
make list-suites
```

### CI/CD Integration

```bash
# CI-friendly test execution
make ci-test

# YAML suite testing for CI
make ci-test-yaml SUITE=test_suites/production/mrgb_blog_test_suite.yaml
```

## 🔍 Test Development

### Writing Custom Tests

```python
import pytest
import allure
from tests.conftest import config, browser_manager

@pytest.mark.browser
@allure.feature("Custom Feature")
@allure.story("Custom Test Story")
async def test_custom_functionality(config, browser_manager):
    """Custom test example"""
    with allure.step("Setup test data"):
        # Test setup
        pass
    
    with allure.step("Execute test action"):
        # Test execution
        result = await some_async_operation()
        assert result is not None
    
    with allure.step("Verify results"):
        # Test verification
        allure.attach(str(result), name="Test Result", attachment_type=allure.attachment_type.TEXT)
        assert result.success
```

### Custom Fixtures

```python
# In conftest.py or test files
@pytest.fixture
async def custom_test_data():
    """Provide custom test data"""
    data = await load_test_data()
    yield data
    await cleanup_test_data(data)
```

## 🐛 Troubleshooting

### Common Issues

1. **Allure CLI not found**
   ```bash
   npm install -g allure-commandline
   ```

2. **YAML suite not found**
   ```bash
   python run_pytest.py --list-suites
   ```

3. **Browser issues**
   ```bash
   # Try different browser
   python run_pytest.py --browser firefox
   
   # Use headless mode
   python run_pytest.py --headless
   ```

4. **Async test issues**
   - Ensure `pytest-asyncio` is installed
   - Check `asyncio_mode = auto` in `pytest.ini`

### Debug Mode

```bash
# Verbose output
python run_pytest.py --pytest-args "-v -s"

# Debug specific test
python run_pytest.py --pytest-args "-k test_specific_name -v -s"

# Show local variables on failure
python run_pytest.py --pytest-args "--tb=long -l"
```

## 🔗 Integration with Existing Framework

### Compatibility
- **YAML Test Suites**: Full compatibility maintained
- **Existing Reports**: HTML and Markdown reports still generated
- **Browser Manager**: Reuses existing browser management
- **LLM Integration**: Works with all configured LLM providers

### Migration Path
1. **Phase 1**: Run existing tests through pytest adapter
2. **Phase 2**: Add custom pytest tests for specific scenarios
3. **Phase 3**: Enhance with advanced allure features

### Dual Reporting
Both old and new reporting systems work together:
- **Legacy**: HTML/Markdown reports in `reports/` directory
- **New**: Allure reports in `allure-report/` directory

## 📈 Benefits

### Enhanced Reporting
- **Interactive Reports**: Rich HTML reports with filtering
- **Historical Trends**: Track test performance over time
- **Detailed Analytics**: Test execution statistics
- **Visual Elements**: Screenshots, charts, and graphs

### Better Test Management
- **Test Discovery**: Automatic test case generation from YAML
- **Parallel Execution**: Faster test runs
- **Flexible Filtering**: Run specific test subsets
- **CI/CD Ready**: Easy integration with build pipelines

### Developer Experience
- **Rich Fixtures**: Reusable test components
- **Async Support**: Native async/await test execution
- **Debug Support**: Better error reporting and debugging
- **IDE Integration**: Full pytest IDE support

## 🚀 Next Steps

1. **Install dependencies** and run your first test
2. **Explore allure reports** to understand the new capabilities
3. **Customize configuration** for your specific needs
4. **Write custom tests** for advanced scenarios
5. **Integrate with CI/CD** pipeline

For more information, see the main project documentation and the pytest/allure official documentation.