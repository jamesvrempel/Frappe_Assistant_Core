# Contributing to Claude for Frappe ERP - Desktop Extension

Thank you for your interest in contributing to the Claude Desktop Extension for Frappe ERP! This document provides guidelines for contributing to the **extension package** specifically.

> **Note**: This is the client-side Claude Desktop Extension located in `client_packages/claude-desktop/`. For contributing to the server-side Frappe Assistant Core app, see the [main project repository](https://github.com/clinu/Frappe_Assistant_Core). See [Client Packages Overview](../README.md) for information about other AI platform integrations.

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** installed and available in PATH
- **Claude Desktop** application installed
- **Git** for version control
- A **Frappe/ERPNext instance** for testing (local or remote)
- **Frappe Assistant Core** app installed on your test instance

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/clinu/Frappe_Assistant_Core.git
   cd Frappe_Assistant_Core/client_packages/claude-desktop
   ```

2. **Set up Python Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Install Development Dependencies**
   ```bash
   pip install pytest black flake8 mypy
   ```

4. **Set up Test Configuration**
   ```bash
   # Copy example configuration
   cp config.example.json config.local.json
   
   # Edit config.local.json with your Frappe instance details
   # This file is gitignored for security
   ```

## 🧪 Testing

### Local Testing

1. **Test the Bridge Script**
   ```bash
   # Syntax check
   python -m py_compile server/frappe_assistant_stdio_bridge.py
   
   # Basic functionality test
   python server/frappe_assistant_stdio_bridge.py --test-connection
   ```

2. **Test with Claude Desktop**
   ```bash
   # Validate manifest first
   python -c "import json; json.load(open('manifest.json'))"
   
   # Create a development DXT package (see BUILD.md for detailed instructions)
   zip -r claude-for-frappe-dev.dxt manifest.json server/ requirements.txt icon.png assets/
   
   # Install in Claude Desktop for testing
   # Double-click the DXT file or use Claude Desktop settings
   ```
   
   **📖 For detailed build instructions, see [BUILD.md](BUILD.md)**

3. **Run Automated Tests**
   ```bash
   # Run all tests
   pytest
   
   # Run specific test categories
   pytest tests/test_manifest.py
   pytest tests/test_bridge.py
   ```

### Manual Testing Checklist

Before submitting a PR, manually test these scenarios:

- [ ] **Manifest Validation**: Run validation script from [BUILD.md](BUILD.md)
- [ ] **Connection Test**: Can connect to Frappe instance
- [ ] **Authentication**: API key/secret authentication works
- [ ] **Basic Tools**: Document CRUD operations work
- [ ] **Data Analysis**: Python code execution works
- [ ] **Visualization**: Chart creation functions properly
- [ ] **Search**: Global and DocType search work
- [ ] **Permissions**: Permission-based access is respected
- [ ] **Error Handling**: Graceful error messages for common issues
- [ ] **DXT Package**: Successfully builds and installs in Claude Desktop

## 📝 Code Style

### Python Code Standards

We follow PEP 8 with these specific guidelines:

```python
# Use 4 spaces for indentation
# Maximum line length: 88 characters (Black default)
# Use double quotes for strings
# Use type hints where possible

def example_function(param: str, optional_param: int = 0) -> dict:
    """
    Brief description of the function.
    
    Args:
        param: Description of parameter
        optional_param: Description with default value
        
    Returns:
        Description of return value
    """
    return {"result": param}
```

### Code Formatting

```bash
# Format code with Black
black server/ tests/

# Check code style
flake8 server/ tests/

# Type checking
mypy server/frappe_assistant_stdio_bridge.py
```

### Documentation Standards

- **Docstrings**: Use Google-style docstrings
- **Comments**: Explain why, not what
- **README**: Update if adding new features
- **Changelog**: Add entries for user-facing changes

## 🔧 Development Workflow

### Making Changes

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make Your Changes**
   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run automated tests
   pytest
   
   # Test manually with Claude Desktop
   python scripts/build_dev.py
   # Install and test the development DXT
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new visualization type for pie charts"
   # or
   git commit -m "fix: resolve authentication timeout issue"
   ```

### Commit Message Convention

We use conventional commits:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (no logic changes)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Build process or auxiliary tool changes

### Pull Request Process

1. **Push Your Branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Use the PR template (auto-populated)
   - Describe what you changed and why
   - Link to any related issues
   - Add screenshots for UI changes

3. **PR Review Process**
   - Automated tests must pass
   - At least one reviewer approval required
   - Address any requested changes
   - Maintainer will merge when ready

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues for duplicates
2. Test with the latest version
3. Try to reproduce with minimal steps

### Bug Report Template

```markdown
**Describe the Bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. macOS 14.0]
- Python Version: [e.g. 3.9.1]
- Claude Desktop Version: [e.g. 1.0.0]
- Frappe Version: [e.g. v14.0.0]
- Extension Version: [e.g. 1.0.0]

**Additional Context**
Any other context about the problem.
```

## ✨ Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions you've considered.

**Additional context**
Screenshots, mockups, or other context.
```

## 🏗️ Architecture Guidelines

### Bridge Script Structure

```python
# server/frappe_assistant_stdio_bridge.py structure:

class FrappeAssistantBridge:
    """Main bridge class handling MCP communication"""
    
    def __init__(self):
        """Initialize connection and configuration"""
        
    async def handle_tool_call(self, tool_name: str, args: dict):
        """Handle individual tool executions"""
        
    async def connect_to_frappe(self):
        """Establish connection to Frappe server"""
```

### Adding New Tools

1. **Define Tool in Manifest**
   ```json
   {
     "name": "new_tool_name",
     "description": "Clear description of what the tool does"
   }
   ```

2. **Implement Tool Handler**
   ```python
   async def handle_new_tool(self, args: dict) -> dict:
       """
       Handle the new tool functionality.
       
       Args:
           args: Tool arguments from Claude
           
       Returns:
           Tool execution results
       """
       # Implementation here
   ```

3. **Add Tool to Router**
   ```python
   self.tool_handlers = {
       "new_tool_name": self.handle_new_tool,
       # ... other tools
   }
   ```

### Error Handling Patterns

```python
try:
    # Frappe API call
    result = await frappe_client.get_doc("DocType", "name")
    return {"success": True, "data": result}
    
except FrappePermissionError:
    return {"success": False, "error": "Insufficient permissions"}
    
except FrappeConnectionError:
    return {"success": False, "error": "Cannot connect to Frappe server"}
    
except Exception as e:
    logger.error(f"Unexpected error in tool: {e}")
    return {"success": False, "error": "Internal error occurred"}
```

## 📋 Release Process

> **Note**: Extension releases are coordinated with the main Frappe Assistant Core project releases.

### Version Numbering

The extension version should match the Frappe Assistant Core version for compatibility.

### Release Steps

1. **Update Version**
   ```bash
   # Update version in manifest.json to match main project
   # Update CHANGELOG.md in extension folder
   ```

2. **Test with Main Project**
   ```bash
   # Ensure compatibility with latest Frappe Assistant Core
   cd ../  # Back to main project root
   bench restart
   # Test extension functionality
   ```

3. **Create Extension Package**
   ```bash
   # Build DXT package
   cd Frappe_Assistant_Core/client_packages/claude-desktop
   zip -r claude-for-frappe-v1.1.0.dxt manifest.json server/ requirements.txt icon.png assets/
   # Package is included in main project releases
   ```

## 🤝 Community

### Getting Help

- **Main Project**: [Frappe_Assistant_Core](https://github.com/clinu/Frappe_Assistant_Core) for general questions
- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bugs and feature requests
- **Extension Issues**: Use this for Claude Desktop Extension specific issues
- **Tool Issues**: Use main project for server-side tool issues
- **Email**: jypaulclinton@gmail.com for sensitive issues

### Code of Conduct

We are committed to providing a welcoming and inclusive experience for everyone. Please be:

- **Respectful**: Treat everyone with respect
- **Inclusive**: Welcome newcomers and different perspectives
- **Collaborative**: Work together towards common goals
- **Professional**: Keep discussions focused and constructive

## 📚 Resources

### Development Documentation

- **[BUILD.md](BUILD.md)** - Complete guide to building and validating the extension
- **[Claude Desktop Extensions](https://www.anthropic.com/engineering/desktop-extensions)** - Official Anthropic documentation
- **[Client Packages Overview](../README.md)** - Architecture and future roadmap

### External Resources

- [Frappe Framework Documentation](https://frappeframework.com/docs)
- [Claude Desktop Documentation](https://claude.ai/desktop)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Python Async Programming](https://docs.python.org/3/library/asyncio.html)
- [Extension Examples](https://github.com/anthropics/claude-desktop-examples) - Community examples

### Development Tools

- **Code Editor**: VS Code with Python extension recommended
- **API Testing**: Postman or similar for Frappe API testing
- **Debugging**: Use Python debugger and logging extensively

---

Thank you for contributing to Claude for Frappe ERP! Your contributions help make AI-powered ERP interactions accessible to everyone. 🚀