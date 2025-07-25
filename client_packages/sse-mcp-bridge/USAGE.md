# SSE MCP Bridge for Frappe

A FastAPI-based bridge that enables Claude API to communicate with Frappe servers via Server-Sent Events (SSE) and the Model Context Protocol (MCP).

## 🚀 Quick Start

### 1. Setup Everything
```bash
# Save the setup script as setup.sh and make it executable
chmod +x setup.sh
./setup.sh
```

### 2. Add Bridge Code
Copy the SSE bridge code from the artifact and save it as `sse_mcp_bridge.py`

### 3. Start Server
```bash
./start_server.sh
```

### 4. Test
```bash
python test_bridge.py
```

## 📋 What Gets Created

The setup script creates:
- 📁 `sse-mcp-bridge/` - Project directory
- 🐍 `venv/` - Python virtual environment
- 📦 `requirements.txt` - Python dependencies
- ⚙️ `.env` - Configuration file
- 🚀 `start_server.sh` - Server startup script
- 🧪 `test_bridge.py` - Test script
- 📖 `USAGE.md` - Detailed usage guide

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

```bash
# 1. Create project directory
mkdir sse-mcp-bridge && cd sse-mcp-bridge

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install fastapi uvicorn httpx pydantic python-dotenv

# 4. Add your sse_mcp_bridge.py file

# 5. Start server
uvicorn sse_mcp_bridge:app --host 0.0.0.0 --port 8000
```

## 🌐 Usage with Claude API

```javascript
// Claude API integration
const response = await anthropic.beta.messages.create({
  model: "claude-sonnet-4-20250514",
  messages: [{ role: "user", content: "Get my Frappe data" }],
  mcp_servers: [{
    type: "url",
    url: "https://your-bridge.com/mcp/sse?server_url=https://your-frappe.com",
    name: "frappe-erp",
    authorization_token: "YOUR_FRAPPE_OAUTH_TOKEN"
  }],
  betas: ["mcp-client-2025-04-04"]
});
```

## 🧪 Testing Endpoints

Once the server is running:

**Health Check:**
```bash
curl http://localhost:8000/health
```

**MCP Request:**
```bash
curl -X POST "http://localhost:8000/mcp/request?server_url=https://erptest.promantia.in" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","id":1}'
```

## ⚙️ Configuration

Edit `.env` file:
```bash
HOST=0.0.0.0        # Server host
PORT=8000           # Server port
DEBUG=false         # Debug mode
```

## 🏗️ Architecture

```
Claude API → SSE Bridge → HTTP MCP Server → Frappe
```

**Key Features:**
- ✅ Dynamic Frappe server URLs (multi-tenant)
- ✅ OAuth token pass-through
- ✅ No hardcoded credentials
- ✅ Compatible with Claude API MCP connector

## 📝 Files Overview

| File | Purpose |
|------|---------|
| `setup.sh` | Complete environment setup |
| `start_server.sh` | Start the SSE bridge server |
| `sse_mcp_bridge.py` | Main FastAPI application |
| `test_bridge.py` | Test suite for validation |
| `requirements.txt` | Python dependencies |
| `.env` | Environment configuration |
| `USAGE.md` | Detailed usage instructions |

## 🚀 Production Deployment

For production:

1. **Use HTTPS** (required for Claude API)
2. **Production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker sse_mcp_bridge:app
   ```
3. **Reverse proxy** (nginx, Apache)
4. **Environment variables** for configuration

## 🐛 Troubleshooting

**Port already in use:**
```bash
PORT=8001 ./start_server.sh
```

**Virtual environment issues:**
```bash
rm -rf venv && ./setup.sh
```

**Connection issues:**
- Check firewall settings
- Verify Frappe server accessibility
- Validate OAuth tokens

## 🤝 Support

For issues:
1. Check `USAGE.md` for detailed instructions
2. Run test suite: `python test_bridge.py`
3. Check server logs for errors
4. Verify Frappe server connectivity

## 📜 License

MIT License - See LICENSE file for details