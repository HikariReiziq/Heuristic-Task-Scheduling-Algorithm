#!/usr/bin/env python3
"""
Simple Zero-Dependency Local Web Server for SOKA Dashboard with Live Simulation API.
SOKA Kelas C - Kelompok 4 (ITS 2026).
Serves dashboard.html, team images, and provides /api/run to execute simulations live.
"""

import http.server
import socketserver
import os
import subprocess
import urllib.parse
import json
import webbrowser
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PARENT_IMAGE_DIR = os.path.abspath(os.path.join(DIRECTORY, "..", "image"))
LOCAL_IMAGE_DIR = os.path.join(DIRECTORY, "image")

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Root routing
        if path in ("/", ""):
            self.path = "/dashboard.html"
            return super().do_GET()

        # Live Simulation API endpoint
        if path == "/api/run":
            scenario = query.get("scenario", ["all"])[0]
            valid_scenarios = {"all", "tugas2a", "gocj", "1", "2", "maheswaran"}
            if scenario not in valid_scenarios:
                scenario = "all"

            try:
                cmd = [sys.executable, "run_simulation.py", "--scenario", scenario]
                proc = subprocess.run(
                    cmd,
                    cwd=DIRECTORY,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                output = proc.stdout
                if proc.stderr:
                    output += "\n[STDERR]\n" + proc.stderr

                # Rebuild dashboard with newest results
                import generate_dashboard
                generate_dashboard.build_dashboard()

                response_data = {
                    "status": "success",
                    "scenario": scenario,
                    "returncode": proc.returncode,
                    "output": output
                }
                status_code = 200
            except Exception as e:
                response_data = {
                    "status": "error",
                    "scenario": scenario,
                    "error": str(e),
                    "output": f"Error running simulation: {e}"
                }
                status_code = 500

            resp_bytes = json.dumps(response_data).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp_bytes)
            return

        # Direct image serving handling URL spaces & paths
        if path.startswith("/image/"):
            filename = urllib.parse.unquote(path[len("/image/"):])
            # Check local first, then parent
            target_path = os.path.join(LOCAL_IMAGE_DIR, filename)
            if not os.path.exists(target_path):
                target_path = os.path.join(PARENT_IMAGE_DIR, filename)

            if os.path.exists(target_path) and os.path.isfile(target_path):
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(os.path.getsize(target_path)))
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                with open(target_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        return super().do_GET()


def main():
    os.chdir(DIRECTORY)

    # Ensure dashboard.html is generated
    import generate_dashboard
    generate_dashboard.build_dashboard()

    print(f"\n=======================================================================")
    print(f"  SOKA KELOMPOK 4 - CLOUDSIM TASK SCHEDULING INTERACTIVE DASHBOARD")
    print(f"=======================================================================")
    print(f"  🌐 Dashboard aktif di: http://localhost:{PORT}")
    print(f"  ⚡ Live Simulation API: http://localhost:{PORT}/api/run?scenario=all")
    print(f"  💡 Buka link di atas pada Google Chrome / Firefox untuk presentasi demo.")
    print(f"  Tekan Ctrl+C untuk menghentikan server.")
    print(f"=======================================================================\n")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer dihentikan.")
            sys.exit(0)


if __name__ == "__main__":
    main()
