# -*- coding: utf-8 -*-
"""
4SureERP Login Validation Script
Checks submitted login credentials against PostgreSQL users table
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import psycopg2
import json

PORT = 8070  # Use a different port to avoid conflicts

class LoginHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]

            # Connect to PostgreSQL
            try:
                conn = psycopg2.connect(
                    dbname="4sureERPdb",
                    user="postgres",
                    password="FloRight4u",
                    host="localhost"
                )
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                result = cursor.fetchone()
                conn.close()

                if result:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'success'}).encode())
                else:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'fail'}).encode())

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, LoginHandler)
    print(f"Login server running on port {PORT}...")
    httpd.serve_forever()
