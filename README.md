# Website Testing Automation with Browser-Use

A simple Python automation script that uses the `browser-use` library to test websites with natural language prompts. This project demonstrates how to automate browser actions using AI to perform website testing tasks.

## Features

- **Prompt-based automation**: Describe what you want to test in natural language
- **Website testing**: Automatically navigate and interact with websites
- **Flexible testing**: Support for custom websites and actions
- **Example implementation**: Ready-to-use example for testing windsurf.com blog

## Prerequisites

- Python 3.8 or higher
- Google API key (for Gemini)
- Internet connection

## Installation

1. **Clone or download this project**

2. **Set up virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install
   ```

5. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your Google API key to the `.env` file:
     ```
     GOOGLE_API_KEY=your_actual_api_key_here
     ```

## Usage

### Quick Example: Test Windsurf.com for Wave 11 Articles

```bash
python example_windsurf_test.py
```

This will:
1. Navigate to windsurf.com
2. Look for blog section
3. Search for articles about "Wave 11"
4. Report findings

### Interactive Website Tester

```bash
python website_tester.py
```

This provides an interactive menu where you can:
1. Test windsurf.com blog for Wave 11 articles
2. Perform custom website tests
3. Exit

### Custom Testing Examples

You can test any website with natural language prompts:

```python
from website_tester import WebsiteTester
import asyncio

async def custom_test():
    tester = WebsiteTester()
    
    # Test a news website
    result = await tester.custom_test(
        "https://news.ycombinator.com",
        "Find the top 3 articles and extract their titles and scores"
    )
    print(result)
    
    # Test an e-commerce site
    result = await tester.custom_test(
        "https://example-shop.com",
        "Navigate to the products page and find items under $50"
    )
    print(result)

asyncio.run(custom_test())
```

## How It Works

The script uses the `browser-use` library, which:

1. **Launches a browser** (Chrome/Chromium via Playwright)
2. **Uses AI** (Google Gemini) to understand your natural language instructions
3. **Performs actions** like clicking, typing, scrolling, and extracting data
4. **Returns results** in a structured format

## Configuration Options

### Headless Mode

Run browser in background (no visible window):

```python
tester = WebsiteTester(headless=True)
```

### Different AI Models

You can use different Google models by modifying the model initialization in `website_tester.py`:

```python
# Uses Google Gemini 2.0 Flash Experimental by default
# Can be configured to use other Gemini models
```

## Example Prompts

Here are some example prompts you can use:

- **Blog testing**: "Go to [website] and find articles about [topic]"
- **E-commerce testing**: "Navigate to the products page and find items in the [category] section"
- **Form testing**: "Fill out the contact form with test data and submit it"
- **Search testing**: "Use the search function to look for [term] and report the results"
- **Navigation testing**: "Check if all main navigation links work properly"

## Troubleshooting

### Common Issues

1. **"Google API key not found"**
   - Make sure you've set the `GOOGLE_API_KEY` environment variable
   - Check that your `.env` file is in the correct location

2. **"Playwright browser not found"**
   - Run `playwright install` to download browser binaries

3. **"Module not found" errors**
   - Make sure you've installed all dependencies: `pip install -r requirements.txt`
   - Check that your virtual environment is activated

4. **Browser automation fails**
   - Some websites have anti-bot protection
   - Try running in non-headless mode to see what's happening
   - Check if the website structure has changed

### Debug Mode

Enable debug logging by setting in your `.env` file:
```
BROWSER_USE_LOGGING_LEVEL=debug
```

## Limitations

- Requires Google API access (costs apply)
- Some websites may block automated browsers
- Complex interactions may require more specific prompts
- Rate limits may apply based on your Google API plan

## Contributing

Feel free to improve this script by:
- Adding more example test cases
- Improving error handling
- Adding support for other AI providers
- Creating more specialized testing functions

## License

This project is for educational and testing purposes. Make sure to respect website terms of service when using automated testing.