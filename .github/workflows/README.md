# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the Frappe Assistant Core project.

## Workflows

### test.yml
- **Purpose**: Main CI/CD pipeline for comprehensive testing
- **Triggers**: Push/PR to main and develop branches
- **Jobs**:
  - Test matrix with Python 3.10 and 3.11
  - Full Frappe bench setup
  - MariaDB service for database testing
  - Complete test suite execution with coverage
  - Linting with ruff and mypy

### unit-tests.yml
- **Purpose**: Quick unit test execution for Python file changes
- **Triggers**: Push/PR with Python file changes
- **Jobs**:
  - Focused testing on specific test modules
  - Faster execution for rapid feedback
  - Tests all tool modules that were previously failing

## Local Testing

To run tests locally:

```bash
# Run all tests
bench --site your_site run-tests --app frappe_assistant_core

# Run specific test module
bench --site your_site run-tests --app frappe_assistant_core --module frappe_assistant_core.tests.test_search_tools

# Run with coverage
bench --site your_site run-tests --app frappe_assistant_core --coverage
```

## Troubleshooting

If tests fail due to missing tools:
1. Ensure the core plugin is enabled in Assistant Core Settings
2. Check that the plugin manager has loaded the tools
3. Verify the test setup includes `_ensure_plugins_enabled()` method