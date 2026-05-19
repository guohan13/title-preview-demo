#!/usr/bin/env python3
import json
import os
import socket
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


ROOT_DIR = Path(__file__).resolve().parent
STATE_FILE = ROOT_DIR / ".preview_state.json"
DEFAULT_STATE = {
    "titleText": "智能纪要：文档编辑及环境配置问题讨论 2026年5月13日",
    "mode": "char",
    "maxShrinkLevels": 1,
    "thresholds": {"first": 20, "second": 50},
    "fontSelections": {
        "base": "32-48",
        "baseCustom": 32,
        "mid": "28-40",
        "min": "22-30",
        "midCustom": 28,
        "minCustom": 19,
    },
    "appliedPreset": {"fontSize": 32, "lineHeight": 48},
    "updatedAt": 0,
}
def load_state():
    if not STATE_FILE.exists():
        return DEFAULT_STATE.copy()
    try:
        with STATE_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_STATE.copy()


def save_state(state):
    with STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False)


def _collect_candidate_ips():
    candidates = []

    def add_candidate(value):
        if not value or value.startswith("127.") or value == "0.0.0.0":
            return
        if value not in candidates:
            candidates.append(value)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            add_candidate(sock.getsockname()[0])
    except OSError:
        pass

    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            add_candidate(ip)
    except OSError:
        pass

    return candidates


def get_mobile_preview_url(port, request_headers=None):
    public_base_url = os.environ.get("PUBLIC_BASE_URL", "").strip()
    if public_base_url:
        parts = urlsplit(public_base_url)
        scheme = parts.scheme or "https"
        netloc = parts.netloc or parts.path
        return urlunsplit((scheme, netloc, "/mobile-preview.html", "", ""))

    if request_headers:
        host = request_headers.get("Host", "").strip()
        forwarded_proto = request_headers.get("X-Forwarded-Proto", "").strip() or "http"
        if host and "localhost" not in host and not host.startswith("127.0.0.1"):
            return f"{forwarded_proto}://{host}/mobile-preview.html"

    candidates = _collect_candidate_ips()
    host = candidates[0] if candidates else "localhost"
    return f"http://{host}:{port}/mobile-preview.html"


class PreviewRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/healthz":
            payload = b"ok"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)
            return
        if self.path == "/api/state":
            state = load_state()
            payload = json.dumps(state, ensure_ascii=False).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)
            return
        if self.path == "/api/mobile-preview-url":
            payload = json.dumps(
                {
                    "mobilePreviewUrl": get_mobile_preview_url(self.server.server_address[1], self.headers),
                },
                ensure_ascii=False,
            ).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)
            return

        super().do_GET()

    def do_POST(self):
        if self.path != "/api/state":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            state = json.loads(raw_body.decode("utf-8"))
            save_state(state)
        except (OSError, ValueError, json.JSONDecodeError):
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON body")
            return

        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()


def main():
    host = os.environ.get("PREVIEW_HOST", "0.0.0.0")
    port = int(os.environ.get("PREVIEW_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), PreviewRequestHandler)
    print(f"Serving preview on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
