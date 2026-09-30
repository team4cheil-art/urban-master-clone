"""Vercel Python serverless function: GET /api/search?query=..."""
import json
import os
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

VWORLD_KEY = os.environ.get("VWORLD_KEY", "")


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        query = (qs.get("query") or [""])[0]

        if not query:
            return self._send_json(400, {"error": "query param required"})
        if not VWORLD_KEY:
            return self._send_json(500, {"error": "VWORLD_KEY not configured"})

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
