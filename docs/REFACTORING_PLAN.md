# BrowserTest AI - Refactoring Plan

## Issues Identified

### 1. Over-engineered YAML Schema
**Problem**: Current implementation has explicit actions and assertions with selectors, which contradicts the natural language approach of browser-use.

**Solution**: Simplify to prompt-based testing where:
- Each test case has a natural language prompt
- LLM figures out the actions using browser-use
- Assertions are also natural language descriptions
- Remove explicit selector-based actions/assertions

### 2. Unnecessary Nested Structure
**Problem**: Code is nested inside `browsertest_ai/` when we're already in the `ai-automation` project.

**Solution**: Flatten structure:
```
ai-automation/
├── config/           # Configuration management
├── llm_integration/  # LLM providers
├── test_engine/      # Core test execution
├── test_suites/      # YAML test files
├── reports/          # Generated reports
└── main.py           # CLI entry point
```

### 3. Poor File Organization
**Problem**: YAML files scattered in root directory.

**Solution**: Create dedicated `test_suites/` directory with organized structure:
```
test_suites/
├── examples/
│   ├── basic_navigation.yaml
│   └── ecommerce_flow.yaml
├── production/
└── staging/
```

## Simplified YAML Schema

### New Test Case Structure
```yaml
name: "E-commerce Test Suite"
description: "Test online shopping workflow"
base_url: "https://example-shop.com"

tests:
  - name: "Product Search and Purchase"
    prompt: |
      Navigate to the homepage, search for 'laptop', 
      click on the first result, add it to cart, 
      and proceed to checkout. Verify the item is in cart.
    
    success_criteria: |
      - Product appears in search results
      - Item successfully added to cart
      - Checkout page loads correctly
    
    timeout: 60
    browser: chrome
    headless: false
```

### Key Changes
- **prompt**: Natural language description of what to test
- **success_criteria**: Natural language assertions
- **No explicit actions/assertions**: Let LLM handle the details
- **Simplified configuration**: Focus on essential settings

## Implementation Steps

1. **Flatten Directory Structure**
   - Move modules from `browsertest_ai/` to root
   - Update all imports
   - Create `test_suites/` directory

2. **Simplify YAML Schema**
   - Remove ActionStep and AssertionStep classes
   - Simplify TestCase to prompt-based approach
   - Update YAMLLoader for new schema

3. **Update Integration Layer**
   - Modify browser-use integration for prompt-only approach
   - Remove action/assertion parsing
   - Focus on natural language processing

4. **Reorganize Test Files**
   - Move YAML files to `test_suites/`
   - Create example categories
   - Update file references

This refactoring will make the framework much more aligned with browser-use's natural language capabilities and easier to use.