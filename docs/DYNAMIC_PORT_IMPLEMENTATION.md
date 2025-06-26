# Dynamic Port Detection Implementation

## Overview

The Assistant Core previously had a configurable `server_port` field, but since the MCP server runs as part of the Frappe application, it should use the same port as Frappe itself. This document describes the implementation of dynamic port detection.

## Problem Solved

**Original Issue**: The server port field was hardcoded to 8000, which would fail if Frappe was running on a different port (e.g., 3000, 8080, etc.).

**Solution**: Implemented dynamic port detection that automatically discovers Frappe's actual running port from configuration files.

## Implementation Details

### Port Detection Logic

The `get_frappe_port()` function uses a multi-method approach:

1. **Frappe Configuration**: Checks `frappe.conf.webserver_port` if available
2. **Bench Configuration**: Traverses up directory tree to find `sites/common_site_config.json`
3. **Site-specific Configuration**: Checks individual site config files
4. **Environment Variable**: Falls back to `FRAPPE_SITE_PORT` environment variable
5. **Default Fallback**: Uses port 8000 as final fallback

### Files Modified

#### `start_server.py`
- Added `get_frappe_port()` function with robust directory traversal
- Updated server startup to use detected port instead of hardcoded value
- Improved error handling and logging

#### `utils/dashboard.py` 
- Added matching `get_frappe_port()` function for dashboard utilities
- Updated dashboard data to show detected port

#### `assistant_core/server.py`
- Added port detection for server status reporting
- Updated status messages to show detected port

#### Tests
- Added comprehensive tests in `test_assistant_core_settings.py`
- Includes boundary testing and validation

### Configuration File Discovery

The implementation searches for configuration in this order:

```
/path/to/bench/
├── sites/
│   ├── common_site_config.json ← Primary source
│   └── [site-name]/
│       └── site_config.json ← Site-specific override
```

### Example Configuration Files

**common_site_config.json**:
```json
{
  "webserver_port": 8080,
  "developer_mode": true,
  "default_site": "my-site"
}
```

**site_config.json** (site-specific):
```json
{
  "webserver_port": 3000,
  "db_name": "my_site_db"
}
```

## Testing

### Test Coverage

1. **Port Detection Tests**: Verify correct port detection from various sources
2. **Fallback Tests**: Ensure graceful fallback to default when config missing
3. **Boundary Tests**: Validate port ranges and error handling
4. **Integration Tests**: Confirm server startup works with detected ports

### Test Results

All test cases pass:
- ✅ Port 8080 detection
- ✅ Port 3000 detection  
- ✅ Port 8000 detection
- ✅ Fallback to default when no config

## Usage Examples

### Standard Frappe Setup (Port 8000)
```bash
# common_site_config.json
{
  "webserver_port": 8000
}
```
**Result**: Assistant Core detects and uses port 8000

### Development Setup (Port 8080)
```bash
# common_site_config.json
{
  "webserver_port": 8080,
  "developer_mode": true
}
```
**Result**: Assistant Core detects and uses port 8080

### Production Setup (Port 80 with Nginx)
```bash
# Environment variable
export FRAPPE_SITE_PORT=80

# Or in site config
{
  "webserver_port": 80
}
```
**Result**: Assistant Core detects and uses port 80

## Benefits

1. **Automatic Configuration**: No manual port configuration needed
2. **Environment Flexibility**: Works with any Frappe port setup
3. **Robust Fallbacks**: Multiple detection methods ensure reliability
4. **Zero Configuration**: Works out-of-the-box with standard Frappe setups
5. **Production Ready**: Handles various deployment scenarios

## Migration Notes

### For Existing Installations

- The `server_port` field has been completely removed from the DocType
- No migration needed - port detection is automatic
- Existing functionality continues to work seamlessly

### For New Installations

- No port configuration required
- Assistant Core automatically uses Frappe's port
- Works with any standard Frappe/ERPNext setup

## Troubleshooting

### If Port Detection Fails

1. **Check Configuration Files**: Ensure `common_site_config.json` exists with `webserver_port`
2. **Verify Directory Structure**: Must be run from within Frappe bench directory
3. **Check Environment**: Set `FRAPPE_SITE_PORT` environment variable as fallback
4. **Review Logs**: Port detection logs show which method was used

### Debug Information

Enable debug logging to see port detection process:
```python
# Will show:
# - Current directory
# - Config files checked
# - Port source (config/env/default)
# - Final detected port
```

## Future Enhancements

- Add support for SSL port detection
- Include port validation and availability checking
- Add configuration caching for performance
- Support for multiple site configurations

---

This implementation ensures Assistant Core seamlessly integrates with any Frappe setup regardless of port configuration, providing a robust and flexible solution for all deployment scenarios.