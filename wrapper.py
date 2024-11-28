import subprocess
import threading
import time
import signal
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

# Configuration
TIMEOUT_MINUTES = int(os.getenv('TIMEOUT_MINUTES', '5'))
TIMEOUT_SECONDS = TIMEOUT_MINUTES * 60
PROXY_PORT = 8080
LANGFLOW_PORT = 8000

print(f"Starting with {TIMEOUT_MINUTES} minute timeout")

# Track the last activity time
last_request_time = time.time()

class ProxyHandler(BaseHTTPRequestHandler):
    def is_health_check(self):
        # Fly.io health checks are GET requests to /health or /healthcheck
        return (self.command == 'GET' and 
                (self.path == '/health' or self.path == '/healthcheck'))

    def handle_request(self):
        global last_request_time
        
        # Only update last_request_time if this is not a health check
        if not self.is_health_check():
            last_request_time = time.time()
            print(f"Activity detected at {time.strftime('%Y-%m-%d %H:%M:%S')} - Path: {self.path}")
        else:
            print(f"Health check received at {time.strftime('%Y-%m-%d %H:%M:%S')} - Ignoring for activity tracking")
        
        target_url = f'http://localhost:{LANGFLOW_PORT}{self.path}'
        
        try:
            # Forward the request to Langflow
            headers = {key: value for key, value in self.headers.items() if key.lower() != 'host'}
            
            # Get request body for POST/PUT/PATCH requests
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Forward the request
            response = requests.request(
                method=self.command,
                url=target_url,
                headers=headers,
                data=body,
                stream=True
            )
            
            # Send response back to client
            self.send_response(response.status_code)
            
            # Forward response headers
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.end_headers()
            
            # Stream response body
            for chunk in response.iter_content(8192):
                self.wfile.write(chunk)
                
        except Exception as e:
            print(f"Error proxying request: {e}")
            self.send_error(502, f'Proxy Error: {str(e)}')
    
    def do_GET(self): self.handle_request()
    def do_POST(self): self.handle_request()
    def do_PUT(self): self.handle_request()
    def do_DELETE(self): self.handle_request()
    def do_OPTIONS(self): self.handle_request()
    def do_HEAD(self): self.handle_request()
    def do_PATCH(self): self.handle_request()  # Added PATCH support

def run_proxy_server():
    server = HTTPServer(('0.0.0.0', PROXY_PORT), ProxyHandler)
    server.serve_forever()

def check_inactivity():
    while True:
        time.sleep(60)  # Check every minute
        elapsed = time.time() - last_request_time
        print(f"Time since last non-health-check request: {int(elapsed/60)} minutes")
        
        if elapsed >= TIMEOUT_SECONDS:
            print(f"No non-health-check requests for {TIMEOUT_MINUTES} minutes, shutting down...")
            sys.exit(0)

def run_langflow():
    # Start Langflow on a different port
    cmd = [
        "langflow", "run",
        "--host", "localhost",
        "--port", str(LANGFLOW_PORT)
    ]
    
    process = subprocess.Popen(cmd)
    
    # Wait for Langflow to start
    time.sleep(5)
    
    # Start the proxy server in a separate thread
    proxy_thread = threading.Thread(target=run_proxy_server, daemon=True)
    proxy_thread.start()
    
    # Start the inactivity checker in a separate thread
    checker_thread = threading.Thread(target=check_inactivity, daemon=True)
    checker_thread.start()
    
    def handle_sigterm(signum, frame):
        print("Received SIGTERM signal")
        process.terminate()
        process.wait()
        print("Clean shutdown complete")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, handle_sigterm)
    
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        sys.exit(0)

if __name__ == "__main__":
    run_langflow()
