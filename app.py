"""
Minimal HTTP server for the React dashboard.
Serves dist/ as static files, and /data.json -> output/data.json
so the pipeline can update data without rebuilding.
"""
import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from functools import partial

BASE_DIR = Path(__file__).parent
DIST_DIR = BASE_DIR / "dist"
OUTPUT_DATA = BASE_DIR / "output" / "data.json"
FALLBACK_DATA = DIST_DIR / "data.json"


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve pipeline data instead of the bundled copy
        if self.path.split("?")[0] == "/data.json":
            data_path = OUTPUT_DATA if OUTPUT_DATA.exists() else FALLBACK_DATA
            if data_path.exists():
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(data_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            self.send_error(404, "data.json not found")
            return

        # SPA fallback: unknown paths get index.html
        rel = self.path.lstrip("/").split("?")[0]
        if rel and not (DIST_DIR / rel).is_file():
            self.path = "/index.html"

        return super().do_GET()


def main():
    port = int(os.environ.get("PORT", 8501))
    handler = partial(DashboardHandler, directory=str(DIST_DIR))
    server = HTTPServer(("0.0.0.0", port), handler)
    print(f"Dashboard server running on http://0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()