#!/usr/bin/env python3
"""Lightweight, standalone HTTP sync server for TikTok Live Auto Liker.

Zero external dependencies (uses standard library http.server).
Can be deployed on a VPS, Raspberry Pi, Docker, or home server.

Usage:
    python sync_server.py [--port 8765] [--api-key mysecretkey] [--data-file sync_data.json]
"""

import os
import sys
import json
import time
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional

try:
    from sync_manager import SyncBundle, merge_bundles
except ImportError:
    # Minimal fallback if sync_manager is in a different directory
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from sync_manager import SyncBundle, merge_bundles

DATA_FILE = "sync_data.json"
API_KEY: Optional[str] = None


class SyncHTTPRequestHandler(BaseHTTPRequestHandler):
    server_version = "TikTokLiveSyncServer/1.0"

    def _send_json(self, status_code: int, data: dict):
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-API-Key")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(payload)

    def _is_authorized(self) -> bool:
        if not API_KEY:
            return True
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            if token == API_KEY:
                return True
        api_key_header = self.headers.get("X-API-Key", "").strip()
        if api_key_header == API_KEY:
            return True
        return False

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-API-Key")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed_path = self.path.split("?")[0].rstrip("/")

        if parsed_path in ("", "/health"):
            self._send_json(200, {
                "status": "online",
                "service": "TikTok Live Auto-Liker Sync Server",
                "timestamp": time.time(),
                "auth_required": bool(API_KEY)
            })
            return

        if parsed_path == "/api/sync":
            if not self._is_authorized():
                self._send_json(401, {"error": "Unauthorized: Invalid or missing API key."})
                return

            if not os.path.exists(DATA_FILE):
                self._send_json(200, {
                    "version": 1,
                    "timestamp": time.time(),
                    "favorites": {},
                    "settings": {},
                    "tombstones": {}
                })
                return

            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    bundle_data = json.load(f)
                self._send_json(200, bundle_data)
            except Exception as e:
                self._send_json(500, {"error": f"Failed to read data file: {e}"})
            return

        self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        parsed_path = self.path.split("?")[0].rstrip("/")

        if parsed_path == "/api/sync":
            if not self._is_authorized():
                self._send_json(401, {"error": "Unauthorized: Invalid or missing API key."})
                return

            try:
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8")
                incoming_data = json.loads(body)
                incoming_bundle = SyncBundle.from_dict(incoming_data)
            except Exception as e:
                self._send_json(400, {"error": f"Invalid JSON payload: {e}"})
                return

            # If server has existing bundle, merge them with CRDT LWW
            if os.path.exists(DATA_FILE):
                try:
                    with open(DATA_FILE, "r", encoding="utf-8") as f:
                        server_data = json.load(f)
                    server_bundle = SyncBundle.from_dict(server_data)
                    merged_bundle, _, _ = merge_bundles(server_bundle, incoming_bundle)
                except Exception:
                    merged_bundle = incoming_bundle
            else:
                merged_bundle = incoming_bundle

            # Write merged bundle atomically
            try:
                temp_file = DATA_FILE + ".tmp"
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(merged_bundle.to_dict(), f, indent=2)
                os.replace(temp_file, DATA_FILE)
                self._send_json(200, {
                    "status": "success",
                    "favorites_count": len(merged_bundle.favorites),
                    "timestamp": merged_bundle.timestamp
                })
            except Exception as e:
                self._send_json(500, {"error": f"Failed to save sync bundle: {e}"})
            return

        self._send_json(404, {"error": "Endpoint not found"})

    def log_message(self, format, *args):
        # Clean terminal logging
        sys.stdout.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {args[0]} {args[1]} -> {args[2]}\n")
        sys.stdout.flush()


def run_server(host: str = "0.0.0.0", port: int = 8765, api_key: Optional[str] = None, data_file: str = "sync_data.json"):
    global DATA_FILE, API_KEY
    DATA_FILE = os.path.abspath(data_file)
    API_KEY = api_key

    server_address = (host, port)
    httpd = HTTPServer(server_address, SyncHTTPRequestHandler)
    print("=" * 60)
    print("  TikTok Live Auto-Liker — Central Sync Server")
    print("=" * 60)
    print(f"  Listening on: http://{host}:{port}")
    print(f"  Data File:    {DATA_FILE}")
    print(f"  Auth:         {'API Key Enabled' if API_KEY else 'Open (No API Key)'}")
    print("=" * 60)
    print("  Endpoints:")
    print(f"    - GET  http://{host}:{port}/health")
    print(f"    - GET  http://{host}:{port}/api/sync")
    print(f"    - POST http://{host}:{port}/api/sync")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down sync server...")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TikTok Live Auto Liker Central Sync Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8765, help="Port to listen on (default: 8765)")
    parser.add_argument("--api-key", default=None, help="Optional secret API key for authorization")
    parser.add_argument("--data-file", default="sync_data.json", help="Path to JSON file to persist sync data")
    args = parser.parse_args()

    run_server(host=args.host, port=args.port, api_key=args.api_key, data_file=args.data_file)
