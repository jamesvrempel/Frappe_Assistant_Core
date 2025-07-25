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
- **Auto-fixable**: ~3,278 (mostly whitespace and import sorting)
- **Critical issues**: 13 (undefined names in visualization tools)

## Known Issues

1. ✅ **Template files**: Fixed by excluding `docs/templates/` from linting
2. **Import issues**: Some modules use string type annotations (`"pd.DataFrame"`) without importing pandas
3. **Undefined names**: 13 critical issues in visualization and chart tools:
   - `plt` (matplotlib.pyplot) used without import
   - `sns` (seaborn) used without import  
   - `pd` (pandas) used in string annotations
   - `np` (numpy) used without import

## Critical Issues to Fix

The following files have undefined name errors that should be fixed:

```
frappe_assistant_core/plugins/data_science/tools/create_visualization.py
- Lines 311, 313, 317: sns, plt used without import
- Multiple lines: pd used in string annotations

frappe_assistant_core/plugins/visualization/utils/chart_suggestions.py  
- Lines 254, 255: np used without import
```

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