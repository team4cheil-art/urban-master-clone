"""Vercel Python serverless function: GET /api/geocode?address=...

Proxies to Kakao Local address search so the REST key stays server-side.
Set KAKAO_REST_KEY as an Environment Variable in the Vercel project settings.
"""
import json
import os
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

KAKAO_REST_KEY = os.environ.get("KAKAO_REST_KEY", "")


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
        if not KAKAO_REST_KEY:
            return self._send_json(500, {"error": "KAKAO_REST_KEY not configured"})

        url = (
            "https://dapi.kakao.com/v2/local/search/address.json"
            f"?query={urllib.parse.quote(address)}"
        )
        req = urllib.request.Request(url, headers={"Authorization": f"KakaoAK {KAKAO_REST_KEY}"})
        try:
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            return self._send_json(502, {"ok": False, "error": str(e)})

        docs = data.get("documents") or []
        if not docs:
            return self._send_json(200, {"ok": False, "raw": data})

        doc = docs[0]
        road = doc.get("road_address") or {}
        label = road.get("address_name") or doc.get("address_name") or address
        result = {
            "refined": {"text": label},
            "result": {"point": {"x": doc.get("x"), "y": doc.get("y")}},
        }
        return self._send_json(200, {"ok": True, "result": result})
