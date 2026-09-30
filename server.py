"""Local dev server for the urban-master clone.

Serves the static site and proxies address-geocoding requests to VWorld,
so the API key stays server-side and the browser never sees it (and we
sidestep VWorld's lack of CORS headers for browser fetches).
"""
import json
import os
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 5500


def load_env():
    env = {}
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


ENV = load_env()
VWORLD_KEY = ENV.get("VWORLD_KEY", "")


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/geocode":
            return self.handle_geocode(parsed)
        if parsed.path == "/api/search":
            return self.handle_search(parsed)

        return self.serve_static()

    def handle_geocode(self, parsed):
        qs = urllib.parse.parse_qs(parsed.query)
        address = (qs.get("address") or [""])[0]
        if not address:
            return self._send_json(400, {"error": "address query param required"})
        if not VWORLD_KEY:
            return self._send_json(500, {"error": "VWORLD_KEY not configured on server"})

        results = {}
        for addr_type in ("road", "parcel"):
            url = (
                "https://api.vworld.kr/req/address?service=address&request=getcoord"
                f"&key={VWORLD_KEY}&type={addr_type}&format=json"
                f"&address={urllib.parse.quote(address)}"
            )
            try:
                with urllib.request.urlopen(url, timeout=6) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                status = data.get("response", {}).get("status")
                if status == "OK":
                    results[addr_type] = data["response"]
            except Exception as e:  # noqa: BLE001
                results[addr_type + "_error"] = str(e)

        if "road" in results or "parcel" in results:
            best = results.get("road") or results.get("parcel")
            return self._send_json(200, {"ok": True, "result": best, "raw": results})
        return self._send_json(200, {"ok": False, "raw": results})

    def handle_search(self, parsed):
        qs = urllib.parse.parse_qs(parsed.query)
        query = (qs.get("query") or [""])[0]
        if not query:
            return self._send_json(400, {"error": "query param required"})
        if not VWORLD_KEY:
            return self._send_json(500, {"error": "VWORLD_KEY not configured on server"})

        url = (
            "https://api.vworld.kr/req/search?service=search&request=search"
            f"&key={VWORLD_KEY}&query={urllib.parse.quote(query)}"
            "&type=address&format=json&size=5"
        )
        try:
            with urllib.request.urlopen(url, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return self._send_json(200, {"ok": True, "raw": data})
        except Exception as e:  # noqa: BLE001
            return self._send_json(200, {"ok": False, "error": str(e)})

    def serve_static(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            path = "/index.html"
        fs_path = os.path.normpath(os.path.join(ROOT, path.lstrip("/")))
        if not fs_path.startswith(ROOT) or not os.path.isfile(fs_path):
            self.send_response(404)
            self._cors()
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        ctype = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".svg": "image/svg+xml",
            ".png": "image/png",
        }.get(os.path.splitext(fs_path)[1], "application/octet-stream")

        with open(fs_path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print(f"Serving {ROOT} on http://localhost:{PORT}  (VWORLD_KEY {'set' if VWORLD_KEY else 'MISSING'})")
    ThreadingHTTPServer(("localhost", PORT), Handler).serve_forever()
