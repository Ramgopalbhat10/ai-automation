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
if "%1"=="clean-preserve-history" goto clean-preserve-history
if "%1"=="preserve-history" goto preserve-history
if "%1"=="generate-report" goto generate-report
if "%1"=="generate-report-with-history" goto generate-report-with-history
if "%1"=="generate-timestamped-report" goto generate-timestamped-report
if "%1"=="archive-results" goto archive-results
if "%1"=="serve-report" goto serve-report
if "%1"=="list-suites" goto list-suites
if "%1"=="ci-test" goto ci-test
if "%1"=="ci-test-yaml" goto ci-test-yaml
if "%1"=="test-with-history" goto test-with-history
goto help

:help
echo BrowserTest AI - Pytest ^& Allure Integration
echo ============================================
echo.
echo Available commands:
echo   install                      - Install dependencies
echo   test                         - Run all tests
echo   test-unit                    - Run unit tests only
echo   test-integration             - Run integration tests only
echo   test-yaml                    - Run YAML suite tests
echo   test-all                     - Run all tests with report generation
echo   test-and-serve               - Run tests and start allure server
echo   quick-test                   - Run quick test with default suite
echo   test-parallel                - Run tests in parallel
echo   clean-results                - Clean test results and reports
echo   clean-preserve-history       - Clean results but preserve test history
echo   preserve-history             - Copy history from previous report
echo   generate-report              - Generate allure HTML report (no history)
echo   generate-report-with-history - Generate allure HTML report with history
echo   generate-timestamped-report  - Generate timestamped report for archival
echo   archive-results              - Archive current test results
echo   serve-report                 - Start allure server
echo   list-suites                  - List available YAML test suites
echo   ci-test                      - Run CI tests with report
echo   ci-test-yaml                 - Run CI YAML tests with report
echo   test-with-history [type]     - Complete automated workflow with history management
echo.
echo History Management:
echo   For proper test history tracking, use these commands in sequence:
echo   1. run_tests.bat preserve-history     (before running new tests)
echo   2. run_tests.bat test-yaml            (run your tests)
echo   3. run_tests.bat generate-report-with-history (generate report with history)
echo.
echo Examples:
echo   run_tests.bat test-yaml
echo   run_tests.bat test-and-serve
echo   run_tests.bat test-parallel
echo   run_tests.bat clean-preserve-history
echo   run_tests.bat generate-report-with-history
echo   run_tests.bat test-with-history yaml
echo   run_tests.bat test-with-history parallel
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

:preserve-history
echo Preserving test history...
if exist allure-report\history (
    if not exist allure-results mkdir allure-results
    xcopy /e /i /y allure-report\history allure-results\history >nul
    echo History preserved from previous report
) else (
    echo No previous history found
)
goto end

:clean-preserve-history
echo Cleaning test results while preserving history...
if exist allure-report\history (
    if not exist allure-results mkdir allure-results
    xcopy /e /i /y allure-report\history allure-results\history >nul
)
if exist allure-results (
    for /f "delims=" %%i in ('dir /b /a-d allure-results 2^>nul ^| findstr /v "history"') do del /q "allure-results\%%i" 2>nul
)
if exist allure-report rmdir /s /q allure-report
if exist .pytest_cache rmdir /s /q .pytest_cache
if exist reports (
    del /q reports\*.html 2>nul
    del /q reports\*.md 2>nul
)
echo Cleanup completed with history preserved!
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

:generate-report-with-history
echo Generating allure HTML report with history...
if not exist allure-results (
    echo No allure results found. Run tests first.
    exit /b 1
)
if exist allure-report\history (
    if not exist allure-results\history (
        echo Copying history from previous report...
        xcopy /e /i /y allure-report\history allure-results\history >nul
    )
)
allure generate allure-results -o allure-report --clean
echo Report with history generated: allure-report/index.html
goto end

:generate-timestamped-report
echo Generating timestamped report...
if not exist allure-results (
    echo No allure results found. Run tests first.
    exit /b 1
)
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,8%_%dt:~8,6%"
if not exist allure-reports-archive mkdir allure-reports-archive
allure generate allure-results -o allure-reports-archive\allure-report-%timestamp%
echo Timestamped report generated: allure-reports-archive/allure-report-%timestamp%/index.html
goto end

:archive-results
echo Archiving current test results...
if not exist allure-results (
    echo No allure results found to archive.
    exit /b 1
)
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,8%_%dt:~8,6%"
if not exist allure-results-archive mkdir allure-results-archive
xcopy /e /i /y allure-results allure-results-archive\allure-results-%timestamp% >nul
echo Results archived: allure-results-archive/allure-results-%timestamp%
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

:test-with-history
set test_type=%2
if "%test_type%"=="" set test_type=yaml
echo ℹ Starting automated test workflow with history management...
echo ℹ Test type: %test_type%

echo ℹ Step 1/6: Preserving test history...
call :preserve-history

echo ℹ Step 2/6: Cleaning old results while preserving history...
call :clean-preserve-history

echo ℹ Step 3/6: Running tests...
if "%test_type%"=="yaml" (
    if "%SUITE%"=="" set SUITE=test_suites/production/mrgb_blog_test_suite.yaml
    set YAML_SUITE=%SUITE%
    python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite"
) else if "%test_type%"=="all" (
    python -m pytest tests/ -v --alluredir=allure-results
) else if "%test_type%"=="unit" (
    python -m pytest tests/ -v --alluredir=allure-results -m "unit"
) else if "%test_type%"=="integration" (
    python -m pytest tests/ -v --alluredir=allure-results -m "integration"
) else if "%test_type%"=="parallel" (
    if "%SUITE%"=="" set SUITE=test_suites/production/mrgb_blog_test_suite.yaml
    set YAML_SUITE=%SUITE%
    python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite" -n 2
) else if "%test_type%"=="quick" (
    set SUITE=test_suites/examples/example_test_suite.yaml
    set YAML_SUITE=%SUITE%
    python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite"
) else (
    echo ℹ Unknown test type '%test_type%', defaulting to YAML tests
    if "%SUITE%"=="" set SUITE=test_suites/production/mrgb_blog_test_suite.yaml
    set YAML_SUITE=%SUITE%
    python -m pytest tests/test_yaml_suites.py -v --alluredir=allure-results -m "yaml_suite"
)

echo ℹ Step 4/6: Generating report with history...
call :generate-report-with-history

echo ℹ Step 5/6: Creating timestamped archive...
call :generate-timestamped-report

echo ℹ Step 6/6: Starting Allure server...
echo ✓ 🎉 Automated workflow completed successfully!
echo ℹ Report available at: allure-report/index.html
echo ℹ Starting server for immediate viewing...
call :serve-report
goto end

:end