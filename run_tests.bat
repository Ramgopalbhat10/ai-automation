@echo off
REM BrowserTest AI - Test Runner for Windows
REM This batch file provides Makefile-like functionality for Windows users

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="install" goto install
if "%1"=="test" goto test
if "%1"=="test-unit" goto test-unit
if "%1"=="test-integration" goto test-integration
if "%1"=="test-yaml" goto test-yaml
if "%1"=="test-all" goto test-all
if "%1"=="test-and-serve" goto test-and-serve
if "%1"=="quick-test" goto quick-test
if "%1"=="test-parallel" goto test-parallel
if "%1"=="clean-results" goto clean-results
if "%1"=="generate-report" goto generate-report
if "%1"=="serve-report" goto serve-report
if "%1"=="list-suites" goto list-suites
if "%1"=="ci-test" goto ci-test
if "%1"=="ci-test-yaml" goto ci-test-yaml
goto help

:help
echo BrowserTest AI - Pytest ^& Allure Integration
echo ============================================
echo.
echo Available commands:
echo   install          - Install dependencies
echo   test             - Run all tests
echo   test-unit        - Run unit tests only
echo   test-integration - Run integration tests only
echo   test-yaml        - Run YAML suite tests
echo   test-all         - Run all tests with report generation
echo   test-and-serve   - Run tests and start allure server
echo   quick-test       - Run quick test with default suite
echo   test-parallel    - Run tests in parallel
echo   clean-results    - Clean test results and reports
echo   generate-report  - Generate allure HTML report
echo   serve-report     - Start allure server
echo   list-suites      - List available YAML test suites
echo   ci-test          - Run CI tests with report
echo   ci-test-yaml     - Run CI YAML tests with report
echo.
echo Examples:
echo   run_tests.bat test-yaml
echo   run_tests.bat test-and-serve
echo   run_tests.bat test-parallel
echo.
echo Environment Variables:
echo   SUITE - Test suite file (default: test_suites/production/mrgb_blog_test_suite.yaml)
goto end

:install
echo Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed successfully!
goto end

:test
echo Running all tests...
python -m pytest tests/ -v --alluredir=allure-results
goto end

:test-unit
echo Running unit tests...
python -m pytest tests/ -v --alluredir=allure-results -m "unit"
goto end

:test-integration
echo Running integration tests...
python -m pytest tests/ -v --alluredir=allure-results -m "integration"
goto end

:test-yaml
echo Running YAML suite tests...
if "%SUITE%"=="" set SUITE=test_suites/production/mrgb_blog_test_suite.yaml
echo Using test suite: %SUITE%
set YAML_SUITE=%SUITE%
python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite"
goto end

:test-all
echo Running all tests with report generation...
call :test
call :generate-report
echo All tests completed with report generation!
goto end

:test-and-serve
echo Running tests and starting allure server...
call :test-yaml
call :generate-report
echo Tests completed! Starting allure server...
allure serve allure-results
goto end

:quick-test
echo Running quick test with default suite...
if "%SUITE%"=="" set SUITE=test_suites/production/mrgb_blog_test_suite.yaml
set YAML_SUITE=%SUITE%
python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite"
goto end

:test-parallel
echo Running tests in parallel...
if "%SUITE%"=="" set SUITE=test_suites/production/mrgb_blog_test_suite.yaml
set YAML_SUITE=%SUITE%
python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite" -n 2
goto end

:clean-results
echo Cleaning test results and reports...
if exist allure-results rmdir /s /q allure-results
if exist allure-report rmdir /s /q allure-report
if exist .pytest_cache rmdir /s /q .pytest_cache
if exist reports (
    del /q reports\*.html 2>nul
    del /q reports\*.md 2>nul
)
echo Cleanup completed!
goto end

:generate-report
echo Generating allure HTML report...
if not exist allure-results (
    echo No allure results found. Run tests first.
    exit /b 1
)
allure generate allure-results -o allure-report --clean
echo Report generated: allure-report/index.html
goto end

:serve-report
echo Starting allure server...
allure serve allure-results
goto end

:list-suites
echo Listing available YAML test suites...
dir /b /s test_suites\*.yaml | sort
goto end

:ci-test
echo Running CI tests...
python -m pytest tests/ -v --alluredir=allure-results --tb=short --strict-markers
call :generate-report
goto end

:ci-test-yaml
echo Running CI YAML tests...
if "%SUITE%"=="" set SUITE=test_suites/production/mrgb_blog_test_suite.yaml
set YAML_SUITE=%SUITE%
python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite" --tb=short --strict-markers
call :generate-report
goto end

:end