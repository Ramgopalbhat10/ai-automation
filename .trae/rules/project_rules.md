## About

This project is **BrowserTest AI** - a modular, intelligent browser automation testing framework that uses the `browser-use` library with LLM integration for natural language test creation and execution.

## Architecture

- **Modular Design**: Organized into core modules (config, test_engine, llm_integration, browser_manager)
- **YAML Configuration**: Tests defined in YAML format with natural language prompts
- **Multi-LLM Support**: Configurable LLM providers (Google Gemini, OpenAI, etc.)
- **Parallel Execution**: Support for concurrent test execution with browser session pooling
- **Environment Management**: Multi-environment support (dev, staging, production)
- **Cross-Browser Testing**: Support for Chrome, Firefox, Safari, Edge

## Development Guidelines

- **Task-Based Development**: Follow tasks.md for structured implementation
- **Incremental Progress**: Complete and evaluate each task before proceeding
- **Backward Compatibility**: Maintain compatibility with existing code during refactoring
- **Testing**: Comprehensive unit and integration testing for all modules

**Important:** For effective use of `browser-use` library, ALWAYS use the context7 MCP server.
