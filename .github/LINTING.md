# Linting and Code Quality

## Overview

This project uses several tools to maintain code quality:

- **Ruff**: Fast Python linter (replacement for flake8, isort, etc.)
- **MyPy**: Static type checker
- **Black**: Code formatter (configured in pyproject.toml)

## Running Linters Locally

### Ruff

```bash
# Check for issues
ruff check .

# Fix auto-fixable issues
ruff check . --fix

# Show statistics
ruff check . --statistics
```

### MyPy

```bash
# Run type checking
mypy . --ignore-missing-imports

# Run with specific module
mypy frappe_assistant_core --ignore-missing-imports
```

### Black (formatting)

```bash
# Check formatting
black . --check

# Apply formatting
black .
```

## Current Status

As of the latest check:
- **Total linting issues**: ~3,551
- **Auto-fixable**: ~3,278
- **Critical issues**: 15 (undefined names and syntax errors)

## Known Issues

1. **Template files**: The template files in `docs/templates/` contain placeholder syntax that causes parsing errors
2. **Import issues**: Some modules use string type annotations that require imports
3. **Whitespace**: Many files have trailing whitespace or blank lines with whitespace

## CI/CD Integration

The GitHub Actions workflows run linting checks on every push and PR:
- Python 3.10 and 3.11 compatibility
- Ruff linting (non-blocking)
- MyPy type checking (non-blocking)

## Recommended Fixes

1. Fix critical undefined name errors in visualization tools
2. Clean up whitespace issues with `ruff check . --fix`
3. Update template files to use valid Python syntax
4. Add proper type imports for string annotations