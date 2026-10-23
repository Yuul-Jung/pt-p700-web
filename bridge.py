#!/usr/bin/env python3
"""Local-only PT-P700 print bridge (experimental)."""
import base64
import io
import json
import os
import shutil
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from PIL import Image

HOST = "127.0.0.1"
PORT = 8765
ORIGINS = {"https://yuul-jung.github.io", "http://localhost:8000", "http://127.0.0.1:8000"}
HEIGHTS = {6: 32, 9: 48, 12: 70, 18: 112, 24: 128}

class Handler(BaseHTTPRequestHandler):
    def reply(self, code, data):
        blob = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        origin = self.headers.get("Origin")
        if origin in ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)

    def allowed(self):
        return self.headers.get("Origin") in ORIGINS

    def do_GET(self):
        if self.path != "/status" or not self.allowed():
            return self.reply(403, {"ok": False, "error": "Not authorized"})
        usb = False
        try:
            for dev in Path("/sys/bus/usb/devices").iterdir():
                vendor = dev / "idVendor"
                product = dev / "idProduct"
                if vendor.exists() and product.exists():
                    if vendor.read_text().strip().lower() == "04f9" and product.read_text().strip().lower() == "2061":
                        usb = True
                        break
        except OSError:
            pass
        self.reply(200, {"ok": True, "usb_detected": usb, "ptouch_print_installed": shutil.which("ptouch-print") is not None})

    def do_OPTIONS(self):
        if not self.allowed():
            return self.reply(403, {"ok": False, "error": "Origin not allowed"})
        self.reply(200, {"ok": True})

    def do_POST(self):
        if self.path != "/print" or not self.allowed():
            return self.reply(403, {"ok": False, "error": "Not authorized"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 2_000_000:
                return self.reply(413, {"ok": False, "error": "Invalid request size"})
            data = json.loads(self.rfile.read(size))
            width = int(data["tape_width_mm"])
            if width not in HEIGHTS:
                return self.reply(400, {"ok": False, "error": "Invalid tape width"})
            png = data["png"]
            if not isinstance(png, str) or not png.startswith("data:image/png;base64,"):
                return self.reply(400, {"ok": False, "error": "PNG data URL required"})
            raw = base64.b64decode(png.split(",", 1)[1], validate=True)
            with Image.open(io.BytesIO(raw)) as image:
                image.load()
                if image.width > 3000 or image.height != HEIGHTS[width]:
                    raise ValueError("Unexpected image dimensions")
                bw = image.convert("L").point(lambda p: 255 if p >= 160 else 0).convert("1")
                if not shutil.which("ptouch-print"):
                    return self.reply(503, {"ok": False, "error": "Install ptouch-print"})
                with tempfile.TemporaryDirectory(prefix="pt-p700-") as td:
                    path = Path(td) / "label.png"
                    bw.save(path, "PNG")
                    result = subprocess.run(
                        ["ptouch-print", "--image", str(path)],
                        capture_output=True, text=True, timeout=40
                    )
                    if result.returncode:
                        return self.reply(502, {"ok": False, "error": (result.stderr or result.stdout)[-700:]})
            self.reply(200, {"ok": True})
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self.reply(400, {"ok": False, "error": str(exc)})
        except subprocess.TimeoutExpired:
            self.reply(504, {"ok": False, "error": "Printer timed out"})
        except Exception as exc:
            self.reply(500, {"ok": False, "error": str(exc)})

if __name__ == "__main__":
    print(f"PT-P700 local print bridge: http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
