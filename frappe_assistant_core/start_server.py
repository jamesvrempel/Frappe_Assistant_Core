#!/usr/bin/env python3


import frappe
import socket
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Constants
DEFAULT_PORT = 8000  # Frappe's default port fallback

class assistantRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests with proper routing"""
        site_name = getattr(self.server, 'site_name', None)
        
        print(f"\n📥 POST {self.path}")
        
        try:
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            request_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            
            # Initialize Frappe context for this request
            frappe.init(site=site_name)
            frappe.connect()
            
            # Set up request context
            frappe.local.request = frappe._dict()
            frappe.request = frappe._dict()
            frappe.request.data = request_data
            
            # Parse JSON if available
            json_data = {}
            if request_data:
                try:
                    json_data = json.loads(request_data.decode('utf-8'))
                    frappe.local.form_dict = json_data
                except:
                    pass
            
            # Handle authentication
            auth_header = self.headers.get('Authorization', '')
            if auth_header.startswith('token '):
                api_key_secret = auth_header[6:]  # Remove 'token ' prefix
                if ':' in api_key_secret:
                    api_key, api_secret = api_key_secret.split(':', 1)
                    print(f"   Received API key: {api_key}")
                    user = self._authenticate_user(api_key, api_secret)
                    print(f"   Authenticating with API key: {api_key}")
                    print(f"   API secret: {'*' * len(api_secret)}")
                    if user:
                        frappe.set_user(user)
                        print(f"   ✅ Authenticated as: {user}")
                    else:
                        print(f"   ❌ Authentication failed")
                        self._send_error_response(401, "Invalid API credentials")
                        return
                else:
                    self._send_error_response(400, "Invalid Authorization header format")
                    return
            else:
                # For endpoints that don't require auth, set guest user
                frappe.set_user("Guest")
                print(f"   Using Guest user")
            
            # Route the request based on path
            if self.path == "/api/method/frappe_assistant_core.api.assistant_api.ping":
                result = self._handle_ping()
            elif self.path == "/api/method/frappe_assistant_core.api.assistant_api.test_auth":
                result = self._handle_test_auth()
            elif self.path == "/api/method/frappe_assistant_core.api.assistant_api.handle_assistant_request":
                result = self._handle_assistant_request()
            else:
                result = {
                    "error": f"Unknown endpoint: {self.path}",
                    "available_endpoints": [
                        "/api/method/frappe_assistant_core.api.assistant_api.ping",
                        "/api/method/frappe_assistant_core.api.assistant_api.test_auth", 
                        "/api/method/frappe_assistant_core.api.assistant_api.handle_assistant_request"
                    ]
                }
            
            # Send successful response
            self._send_json_response(result)
            print(f"   ✅ Response sent successfully")
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Error: {error_msg}")
            self._send_error_response(500, error_msg)
                
        finally:
            # Always clean up Frappe context
            try:
                frappe.destroy()
            except:
                pass

    def _handle_ping(self):
        """Handle ping endpoint"""
        try:
            return {
                "status": "ok",
                "site": frappe.local.site,
                "db_connected": bool(frappe.db),
                "user": frappe.session.user,
                "message": "assistant Server is working",
                "timestamp": frappe.utils.now(),
                "server_info": {
                    "frappe_version": frappe.__version__,
                    "site_path": frappe.local.site_path if hasattr(frappe.local, 'site_path') else None
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Error in ping endpoint"
            }

    def _handle_test_auth(self):
        """Handle test auth endpoint"""
        try:
            if frappe.session.user == "Guest":
                return {
                    "status": "error",
                    "error": "Authentication required",
                    "message": "This endpoint requires authentication"
                }
            
            return {
                "status": "authenticated",
                "site": frappe.local.site,
                "user": frappe.session.user,
                "user_name": frappe.session.get('user_name', 'Unknown'),
                "roles": frappe.get_roles(),
                "db_connected": bool(frappe.db),
                "timestamp": frappe.utils.now()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Error in auth test endpoint"
            }

    def _handle_assistant_request(self):
        """Handle assistant protocol request - this calls the actual assistant API"""
        try:
            print(f"   🔧 Calling actual assistant API handler...")
            
            # Import and call the actual assistant API function
            from frappe_assistant_core.api.assistant_api import handle_assistant_request
            
            # Call the real assistant API handler
            result = handle_assistant_request()
            
            print(f"   ✅ assistant API handler returned: {type(result)}")
            return result
            
        except ImportError as e:
            print(f"   ❌ Failed to import assistant API: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "assistant API module not found",
                    "data": f"Import error: {str(e)}"
                },
                "id": None
            }
        except Exception as e:
            print(f"   ❌ assistant API error: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal error in assistant API",
                    "data": str(e)
                },
                "id": None
            }


    def _send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        
        # Get allowed origins from settings or use localhost default
        try:
            frappe.init(site=getattr(self.server, 'site_name', None))
            frappe.connect()
            settings = frappe.get_single("Assistant Core Settings")
            allowed_origins = settings.allowed_origins if settings.allowed_origins else 'http://localhost:*'
            frappe.destroy()
        except:
            allowed_origins = 'http://localhost:*'
        
        self.send_header('Access-Control-Allow-Origin', allowed_origins)
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2, default=str)
        self.wfile.write(response_json.encode('utf-8'))

    def _send_error_response(self, status_code, message):
        """Send error response"""
        error_data = {
            "error": message,
            "status_code": status_code,
            "timestamp": frappe.utils.now() if hasattr(frappe, 'utils') else None
        }
        self._send_json_response(error_data, status_code)
    
    def _authenticate_user(self, api_key, api_secret):
        """Authenticate user using API key and secret"""
        try:
            # Find user with matching API key
            user_name = frappe.db.get_value("User", {"api_key": api_key}, "name")
            print(f"   Searching for user with API key: {api_key}")
            if not user_name:
                print(f"   ❌ No user found with API key: {api_key}")
                return None
            print(f"   Found user: {user_name} for API key: {api_key}")
            # Get user document
            user = frappe.get_doc("User", user_name)
            print(f"   User document loaded: {user_name}")
            if not user:
                print(f"   ❌ User not found: {user_name}")
                return None
            # Verify API secret
            if user.api_secret == api_secret:
                print(f"   ✅ API secret verified for user: {user_name}")
                return user_name
            else:
                print(f"   ❌ Invalid API secret for user: {user_name}")
                return None
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        
        # Get allowed origins from settings or use localhost default
        try:
            frappe.init(site=getattr(self.server, 'site_name', None))
            frappe.connect()
            settings = frappe.get_single("Assistant Core Settings")
            allowed_origins = settings.allowed_origins if settings.allowed_origins else 'http://localhost:*'
            frappe.destroy()
        except:
            allowed_origins = 'http://localhost:*'
        
        self.send_header('Access-Control-Allow-Origin', allowed_origins)
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Log to console with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def get_frappe_port():
    """Get Frappe's actual running port from configuration"""
    try:
        # Method 1: Try to get from Frappe if available
        try:
            import frappe
            if hasattr(frappe, 'conf') and hasattr(frappe.conf, 'webserver_port'):
                return int(frappe.conf.webserver_port)
        except:
            pass
        
        # Method 2: Try to find common_site_config.json by traversing up
        current_dir = os.getcwd()
        search_dir = current_dir
        
        # Walk up the directory tree to find the bench root (contains sites folder)
        for _ in range(10):  # Limit iterations
            sites_path = os.path.join(search_dir, 'sites')
            config_file = os.path.join(sites_path, 'common_site_config.json')
            
            if os.path.exists(sites_path) and os.path.isdir(sites_path):
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        common_config = json.load(f)
                        if 'webserver_port' in common_config:
                            return int(common_config['webserver_port'])
                break  # Found sites directory, stop searching
            
            parent_dir = os.path.dirname(search_dir)
            if parent_dir == search_dir:  # Reached root
                break
            search_dir = parent_dir
        
        # Method 3: Try site-specific config
        site = get_current_site()
        if site and 'sites_path' in locals():
            site_config_path = os.path.join(sites_path, site, 'site_config.json')
            if os.path.exists(site_config_path):
                with open(site_config_path, 'r') as f:
                    site_config = json.load(f)
                    if 'webserver_port' in site_config:
                        return int(site_config['webserver_port'])
        
        # Method 4: Try to detect from environment
        if 'FRAPPE_SITE_PORT' in os.environ:
            return int(os.environ['FRAPPE_SITE_PORT'])
        
        # Fallback to default
        return DEFAULT_PORT
        
    except Exception as e:
        print(f"Warning: Could not detect Frappe port, using default {DEFAULT_PORT}: {e}")
        return DEFAULT_PORT

def get_current_site():
    """Get the current site name from various sources"""
    
    # Method 1: From environment variable
    site = os.environ.get('FRAPPE_SITE')
    if site:
        return site
    
    # Method 2: From command line argument
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    # Method 3: From current directory (if running from sites/sitename)
    current_dir = os.getcwd()
    if '/sites/' in current_dir:
        site_path = current_dir.split('/sites/')[-1]
        site = site_path.split('/')[0]
        if site and site != 'sites':
            return site
    
    # Method 4: Use default site
    try:
        # Look for bench config
        bench_path = os.getcwd()
        while bench_path != '/':
            config_path = os.path.join(bench_path, 'sites', 'common_site_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    default_site = config_data.get('default_site')
                    if default_site:
                        return default_site
                break
            bench_path = os.path.dirname(bench_path)
        
        # Fallback to looking for any site
        sites_path = os.path.join(bench_path, 'sites')
        if os.path.exists(sites_path):
            for item in os.listdir(sites_path):
                if os.path.isdir(os.path.join(sites_path, item)) and not item.startswith('.'):
                    if item not in ['common_site_config.json', 'assets']:
                        return item
                        
    except Exception as e:
        print(f"Error finding default site: {e}")
    
    return None

class assistantServer(HTTPServer):
    """Custom HTTP server to store site name"""
    def __init__(self, server_address, request_handler, site_name):
        super().__init__(server_address, request_handler)
        self.site_name = site_name

def start_assistant_core(site=None):
    """Start the assistant server on configured port"""
    
    # Get site name
    if not site:
        site = "frappe.assistant"
    
    if not site:
        print("Error: Could not determine site name")
        print("Please specify site name as argument or set FRAPPE_SITE environment variable")
        print("Usage: python start_server.py [site_name]")
        sys.exit(1)
    
    print(f"Starting assistant server for site: {site}")
    
    try:
        # Test initial Frappe connection
        frappe.init(site=site)
        frappe.connect()
        
        # Get settings
        settings = frappe.get_single("Assistant Core Settings")
        
        if not settings.server_enabled:
            print("assistant Server is disabled in settings")
            print("Please enable it in: Setup > Assistant Core Settings")
            frappe.destroy()
            return
        
        port = get_frappe_port()
        
        # Clean up initial connection
        frappe.destroy()
        
        # Check if port is available
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"Port {port} is already in use")
            return
        
        print(f"assistant Server configuration:")
        print(f"  Site: {site}")
        print(f"  Port: {port}")
        print(f"  Max Connections: {settings.max_connections}")
        print(f"  Authentication Required: {settings.authentication_required}")
        print(f"  Rate Limit: {settings.rate_limit} requests/minute")
        
        # Start server with site name
        server = assistantServer(('127.0.0.1', port), assistantRequestHandler, site)
        print(f"\n🚀 assistant Server started successfully!")
        print(f"   Server URL: http://127.0.0.1:{port}")
        print(f"   API Endpoint: http://127.0.0.1:{port}/api/method/frappe_assistant_core.api.assistant_api.handle_assistant_request")
        print(f"   Press Ctrl+C to stop the server\n")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 assistant Server stopped by user")
            server.shutdown()
            
    except Exception as e:
        print(f"Error starting assistant server: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    site_name = None
    
    # Get site from command line argument
    if len(sys.argv) > 1:
        site_name = sys.argv[1]
    
    start_assistant_core(site_name)