# CI Testing Guide

## Local CI Simulation

To test the CI process locally before pushing:

```bash
# 1. Create a temporary directory to simulate CI
mkdir /tmp/ci-test
cd /tmp/ci-test

# 2. Clone your app (simulating GitHub checkout)
git clone /path/to/your/frappe_assistant_core apps/frappe_assistant_core

# 3. Install Bench and initialize
pip install frappe-bench
bench init frappe-bench --frappe-branch version-15 --skip-redis-config-generation

# 4. Setup MariaDB connection (assuming local MariaDB running)
cd frappe-bench
bench set-mariadb-host 127.0.0.1

# 5. Create test site
bench new-site test_site --mariadb-root-password your_password --admin-password admin --no-mariadb-socket

# 6. Setup the app (same as CI)
cp -r ../apps/frappe_assistant_core apps/
echo "frappe_assistant_core" >> sites/apps.txt
pip install -e apps/frappe_assistant_core

# 7. Install app to site
bench --site test_site install-app frappe_assistant_core

# 8. Run tests
bench --site test_site run-tests --app frappe_assistant_core

# 9. Run linting
cd apps/frappe_assistant_core
ruff check . --statistics
mypy . --ignore-missing-imports
```

## CI Workflow Changes Made

### Issue Fixed
- **Problem**: `bench get-app ./apps/frappe_assistant_core` failed because local directories aren't git repositories
- **Solution**: Bypass `bench get-app` and directly:
  1. Copy app to `frappe-bench/apps/`
  2. Add app name to `sites/apps.txt` 
  3. Install with `pip install -e apps/frappe_assistant_core`
  4. Install to site with `bench --site test_site install-app frappe_assistant_core`

### Files Updated
- `.github/workflows/test.yml`: Updated app installation process
- `.github/workflows/unit-tests.yml`: Updated app installation process
- `.github/workflows/lint.yml`: Already working correctly

## Expected CI Behavior

The workflows will now:
1. ✅ Copy the app correctly to the bench directory
2. ✅ Install Python dependencies 
3. ✅ Install the app to the test site
4. ✅ Run the test suite
5. ✅ Report linting results

## Testing Status

- **Workflow Syntax**: ✅ Validated with actionlint
- **Local Testing**: Ready for validation
- **CI Compatibility**: Should now work with GitHub Actions