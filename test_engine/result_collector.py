"""Test result collection and management"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    status: str  # passed, failed, error, skipped
    start_time: datetime
    end_time: datetime
    duration: float
    output: str = ""
    error_message: Optional[str] = None
    screenshots: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.screenshots is None:
            self.screenshots = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        # Convert datetime objects to ISO format
        result['start_time'] = self.start_time.isoformat()
        result['end_time'] = self.end_time.isoformat()
        
        # Convert enum values to strings for JSON serialization
        def convert_enums(obj):
            if hasattr(obj, 'value'):  # Enum object
                return obj.value
            elif isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            return obj
        
        result['metadata'] = convert_enums(result['metadata'])
        return result


class ResultCollector:
    """Collects and manages test results"""
    
    def __init__(self):
        self._results: List[TestResult] = []
    
    def add_result(self, result: TestResult):
        """Add a test result
        
        Args:
            result: Test result to add
        """
        self._results.append(result)
    
    def get_all_results(self) -> List[TestResult]:
        """Get all test results
        
        Returns:
            List of all test results
        """
        return self._results.copy()
    
    def get_results_by_status(self, status: str) -> List[TestResult]:
        """Get results filtered by status
        
        Args:
            status: Status to filter by
            
        Returns:
            List of filtered results
        """
        return [result for result in self._results if result.status == status]
    
    def get_results_by_tag(self, tag: str) -> List[TestResult]:
        """Get results filtered by tag
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of filtered results
        """
        return [
            result for result in self._results 
            if tag in result.metadata.get('tags', [])
        ]
    
    def generate_summary(self, suite_name: str, results: List[TestResult], duration: float) -> Dict[str, Any]:
        """Generate test execution summary
        
        Args:
            suite_name: Name of the test suite
            results: List of test results
            duration: Total execution duration
            
        Returns:
            Summary dictionary
        """
        total_tests = len(results)
        passed_tests = len([r for r in results if r.status == "passed"])
        failed_tests = len([r for r in results if r.status == "failed"])
        error_tests = len([r for r in results if r.status == "error"])
        skipped_tests = len([r for r in results if r.status == "skipped"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Calculate average test duration
        avg_duration = sum(r.duration for r in results) / total_tests if total_tests > 0 else 0
        
        # Find slowest and fastest tests
        slowest_test = max(results, key=lambda r: r.duration) if results else None
        fastest_test = min(results, key=lambda r: r.duration) if results else None
        
        summary = {
            "suite_name": suite_name,
            "execution_time": datetime.now().isoformat(),
            "total_duration": duration,
            "statistics": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "skipped": skipped_tests,
                "success_rate": round(success_rate, 2),
                "average_duration": round(avg_duration, 2)
            },
            "performance": {
                "slowest_test": {
                    "name": slowest_test.test_name if slowest_test else None,
                    "duration": slowest_test.duration if slowest_test else None
                },
                "fastest_test": {
                    "name": fastest_test.test_name if fastest_test else None,
                    "duration": fastest_test.duration if fastest_test else None
                }
            },
            "failed_tests": [
                {
                    "name": result.test_name,
                    "error": result.error_message,
                    "duration": result.duration
                }
                for result in results if result.status in ["failed", "error"]
            ]
        }
        
        return summary
    
    def export_to_json(self, file_path: str, include_summary: bool = True) -> str:
        """Export results to JSON file
        
        Args:
            file_path: Output file path
            include_summary: Whether to include summary statistics
            
        Returns:
            Path to exported file
        """
        # Prepare data for export
        export_data = {
            "export_time": datetime.now().isoformat(),
            "results": [result.to_dict() for result in self._results]
        }
        
        if include_summary:
            total_duration = sum(r.duration for r in self._results)
            summary = self.generate_summary("Export", self._results, total_duration)
            export_data["summary"] = summary
        
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def export_to_html(self, file_path: str) -> str:
        """Export results to HTML report
        
        Args:
            file_path: Output file path
            
        Returns:
            Path to exported file
        """
        # Generate summary
        total_duration = sum(r.duration for r in self._results)
        summary = self.generate_summary("HTML Report", self._results, total_duration)
        
        # Create HTML content
        html_content = self._generate_html_report(summary, self._results)
        
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return file_path
    
    def export_to_markdown(self, file_path: str) -> str:
        """Export results to Markdown report
        
        Args:
            file_path: Output file path
            
        Returns:
            Path to exported file
        """
        # Generate summary
        total_duration = sum(r.duration for r in self._results)
        summary = self.generate_summary("Markdown Report", self._results, total_duration)
        
        # Create Markdown content
        markdown_content = self._generate_markdown_report(summary, self._results)
        
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return file_path
    
    def _generate_markdown_report(self, summary: Dict[str, Any], results: List[TestResult]) -> str:
        """Generate Markdown report content
        
        Args:
            summary: Test summary data
            results: List of test results
            
        Returns:
            Markdown content string
        """
        stats = summary['statistics']
        
        markdown = f"""# BrowserTest AI - Test Report

**Generated on:** {summary['execution_time']}  
**Total Duration:** {summary['total_duration']:.2f} seconds

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Tests | {stats['total_tests']} |
| Passed | {stats['passed']} |
| Failed | {stats['failed']} |
| Errors | {stats['errors']} |
| Skipped | {stats['skipped']} |
| Success Rate | {stats['success_rate']:.1f}% |

## Test Results

"""
        
        for result in results:
            status_emoji = {
                'passed': '✅',
                'failed': '❌',
                'error': '⚠️',
                'skipped': '⏭️'
            }.get(result.status, '❓')
            
            markdown += f"""### {status_emoji} {result.test_name}

**Status:** {result.status.upper()}  
**Duration:** {result.duration:.2f}s  
**Start Time:** {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}  
**End Time:** {result.end_time.strftime('%Y-%m-%d %H:%M:%S')}

"""
            
            if result.error_message:
                markdown += f"""**Error Message:**
```
{result.error_message}
```

"""
            
            if result.output:
                markdown += f"""**Output:**
```
{result.output[:500]}{'...' if len(result.output) > 500 else ''}
```

"""
            
            if result.screenshots:
                markdown += "**Screenshots:**\n"
                for screenshot in result.screenshots:
                    markdown += f"- {screenshot}\n"
                markdown += "\n"
            
            markdown += "---\n\n"
        
        return markdown
    
    def _generate_html_report(self, summary: Dict[str, Any], results: List[TestResult]) -> str:
        """Generate HTML report content
        
        Args:
            summary: Test summary data
            results: List of test results
            
        Returns:
            HTML content string
        """
        stats = summary['statistics']
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BrowserTest AI - Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; margin-bottom: 5px; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .error {{ color: #fd7e14; }}
        .skipped {{ color: #6c757d; }}
        .test-results {{ margin-top: 30px; }}
        .test-item {{ background: white; border: 1px solid #dee2e6; border-radius: 4px; margin-bottom: 10px; padding: 15px; }}
        .test-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .test-name {{ font-weight: bold; }}
        .test-duration {{ color: #6c757d; font-size: 0.9em; }}
        .test-error {{ color: #dc3545; margin-top: 10px; font-family: monospace; background: #f8f9fa; padding: 10px; border-radius: 4px; }}
        .status-badge {{ padding: 4px 8px; border-radius: 4px; color: white; font-size: 0.8em; }}
        .status-passed {{ background-color: #28a745; }}
        .status-failed {{ background-color: #dc3545; }}
        .status-error {{ background-color: #fd7e14; }}
        .status-skipped {{ background-color: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>BrowserTest AI - Test Report</h1>
            <p>Generated on {summary['execution_time']}</p>
            <p>Total Duration: {summary['total_duration']:.2f} seconds</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{stats['total_tests']}</div>
                <div>Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value passed">{stats['passed']}</div>
                <div>Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value failed">{stats['failed']}</div>
                <div>Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value error">{stats['errors']}</div>
                <div>Errors</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['success_rate']}%</div>
                <div>Success Rate</div>
            </div>
        </div>
        
        <div class="test-results">
            <h2>Test Results</h2>
"""
        
        for result in results:
            status_class = f"status-{result.status}"
            html += f"""
            <div class="test-item">
                <div class="test-header">
                    <div class="test-name">{result.test_name}</div>
                    <div>
                        <span class="status-badge {status_class}">{result.status.upper()}</span>
                        <span class="test-duration">{result.duration:.2f}s</span>
                    </div>
                </div>
"""
            
            if result.error_message:
                html += f'<div class="test-error">{result.error_message}</div>'
            
            html += "</div>"
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def clear_results(self):
        """Clear all stored results"""
        self._results.clear()