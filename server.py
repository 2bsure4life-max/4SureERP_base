# -*- coding: utf-8 -*-
"""
4SureERP Minimal Web Server (port 8069)
---------------------------------------
- Serves templates from:  views/templates/
- Serves static   from:   static/
- Friendly routes:
    /                       -> views/templates/index.html (if present) else owner_shell.html
    /owner                  -> views/templates/owner_shell.html
    /owner_shell.html       -> views/templates/owner_shell.html
    /dashboard              -> views/templates/dashboard.html (if present)
    /views/templates/<file> -> serve that template file directly
    /static/<...>           -> serve static assets
    /health                 -> simple JSON health

Notes:
- Supports GET and HEAD
- Threaded (can handle multiple requests)
- Light security headers; adjust CSP as you harden
"""

import http.server
import socketserver
import threading
import os
import json
import mimetypes
from urllib.parse import unquote

# -------------------------
# Config
# -------------------------
PORT = 8069
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "views", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure common types are known
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("application/json", ".json")
mimetypes.add_type("text/html", ".html")
mimetypes.add_type("font/woff2", ".woff2")

def file_exists(path: str) -> bool:
    try:
        return os.path.isfile(path)
    except Exception:
        return False

def safe_join(base: str, rel: str) -> str:
    # Prevent directory traversal
    rel_norm = os.path.normpath(rel).lstrip(os.sep)
    abs_path = os.path.join(base, rel_norm)
    if not abs_path.startswith(os.path.join(base, "")):
        raise PermissionError("Path traversal detected")
    return abs_path

# -------------------------
# HTTP Handler
# -------------------------
class FourSureHandler(http.server.BaseHTTPRequestHandler):
    server_version = "4SureERP/0.1"

    # ---- utilities ----
    def _send_headers(self, status: int, content_type: str, length: int, is_static: bool):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        # Light security
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        # Same-origin by default. If you embed this server in iframes elsewhere, adjust/remove:
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        # (Optional) Basic CSP; loosen as needed for your embeds
        # self.send_header("Content-Security-Policy", "default-src 'self'; frame-ancestors 'self'; frame-src 'self'; img-src 'self' data:;")
        # Caching
        if is_static:
            self.send_header("Cache-Control", "public, max-age=86400")
        else:
            self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _serve_file(self, abs_path: str, explicit_ct: str | None = None, status: int = 200):
        if not file_exists(abs_path):
            self._send_404()
            return

        ctype = explicit_ct or (mimetypes.guess_type(abs_path)[0] or "application/octet-stream")
        is_static = abs_path.startswith(STATIC_DIR)

        if self.command == "HEAD":
            # No body, but correct headers
            size = os.path.getsize(abs_path)
            self._send_headers(status, ctype, size, is_static)
            return

        try:
            with open(abs_path, "rb") as f:
                data = f.read()
            self._send_headers(status, ctype, len(data), is_static)
            self.wfile.write(data)
        except Exception as e:
            self._send_500(f"Read error: {e}")

    def _serve_template(self, name: str):
        path = os.path.join(TEMPLATES_DIR, name)
        self._serve_file(path, "text/html; charset=utf-8")

    def _serve_static(self, rel_path: str):
        try:
            abs_path = safe_join(STATIC_DIR, rel_path)
        except PermissionError:
            self._send_403()
            return
        self._serve_file(abs_path)

    def _send_404(self, msg: str = "Not Found"):
        body = {"error": 404, "message": msg}
        data = json.dumps(body).encode("utf-8")
        self.send_response(404)
        self._send_headers(404, "application/json; charset=utf-8", len(data), False)
        if self.command != "HEAD":
            self.wfile.write(data)

    def _send_403(self, msg: str = "Forbidden"):
        body = {"error": 403, "message": msg}
        data = json.dumps(body).encode("utf-8")
        self.send_response(403)
        self._send_headers(403, "application/json; charset=utf-8", len(data), False)
        if self.command != "HEAD":
            self.wfile.write(data)

    def _send_500(self, msg: str = "Internal Server Error"):
        body = {"error": 500, "message": msg}
        data = json.dumps(body).encode("utf-8")
        self.send_response(500)
        self._send_headers(500, "application/json; charset=utf-8", len(data), False)
        if self.command != "HEAD":
            self.wfile.write(data)

    # ---- routing (shared by GET/HEAD) ----
    def _route(self, path: str):
        # /health
        if path == "/health":
            data = json.dumps({"status": "ok"}).encode("utf-8")
            self._send_headers(200, "application/json; charset=utf-8", len(data), False)
            if self.command != "HEAD":
                self.wfile.write(data)
            return

        # /static/*
        if path.startswith("/static/"):
            return self._serve_static(path[len("/static/"):])

        # /views/templates/<file>
        if path.startswith("/views/templates/"):
            rel = path[len("/views/templates/"):]
            return self._serve_template(rel)

        # Friendly routes
        if path in ("/", "/index", "/index.html"):
            index_path = os.path.join(TEMPLATES_DIR, "index.html")
            if file_exists(index_path):
                return self._serve_template("index.html")
            # Fallback to owner shell if index doesn’t exist
            return self._serve_template("owner_shell.html")

        if path in ("/dashboard", "/dashboard.html"):
            return self._serve_template("dashboard.html")

        if path in ("/owner", "/owner_shell.html"):
            return self._serve_template("owner_shell.html")

        # Default: 404
        self._send_404()

    # ---- HTTP verbs ----
    def do_GET(self):
        path = unquote(self.path.split("?", 1)[0])
        try:
            self._route(path)
        except Exception as e:
            self._send_500(str(e))

    def do_HEAD(self):
        # Same routing, no body; _serve_file respects self.command
        path = unquote(self.path.split("?", 1)[0])
        try:
            self._route(path)
        except Exception as e:
            self._send_500(str(e))

    # Basic access log (optional)
    def log_message(self, fmt, *args):
        try:
            thread = threading.current_thread().name
            print(f"[{self.log_date_time_string()}] [{thread}] {self.address_string()} {self.command} {self.path} -> " + fmt % args)
        except Exception:
            pass

# Threaded server for better concurrency
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def run():
    server_address = ("", PORT)
    httpd = ThreadingHTTPServer(server_address, FourSureHandler)
    print(f"4SureERP server listening on http://0.0.0.0:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run()
