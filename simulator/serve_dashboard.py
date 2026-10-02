#!/usr/bin/env python3
"""
Simple Zero-Dependency Local Web Server for SOKA Dashboard.
Serves dashboard.html on http://localhost:8000 using standard library http.server.
"""

import http.server
import socketserver
import os
import webbrowser
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.path = "/dashboard.html"
        return super().do_GET()

def main():
    os.chdir(DIRECTORY)
    # Check if dashboard.html exists
    if not os.path.exists("dashboard.html"):
        import generate_dashboard
        generate_dashboard.build_dashboard()

    print(f"\n=======================================================================")
    print(f"  SOKA KELOMPOK 4 - CLOUDSIM TASK SCHEDULING INTERACTIVE DASHBOARD")
    print(f"=======================================================================")
    print(f"  🌐 Dashboard aktif di: http://localhost:{PORT}")
    print(f"  💡 Buka link di atas pada Google Chrome / Firefox untuk presentasi demo.")
    print(f"  Tekan Ctrl+C untuk menghentikan server.")
    print(f"=======================================================================\n")

    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer dihentikan.")
            sys.exit(0)

if __name__ == "__main__":
    main()
