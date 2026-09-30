"""Vercel Python serverless function: GET /api/geocode?address=...

Proxies to VWorld's address geocoder so the API key never reaches the
browser and we sidestep VWorld's lack of CORS headers for direct fetch.
Set VWORLD_KEY as an Environment Variable in the Vercel project settings
(never commit it to the repo).
"""
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
        address = (qs.get("address") or [""])[0]

        if not address:
            return self._send_json(400, {"error": "address query param required"})
        if not VWORLD_KEY:
            return self._send_json(500, {"error": "VWORLD_KEY not configured"})

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
                if data.get("response", {}).get("status") == "OK":
                    results[addr_type] = data["response"]
            except Exception as e:  # noqa: BLE001
                results[addr_type + "_error"] = str(e)

        if "road" in results or "parcel" in results:
            best = results.get("road") or results.get("parcel")
            return self._send_json(200, {"ok": True, "result": best, "raw": results})
        return self._send_json(200, {"ok": False, "raw": results})
