"""Small editable partner feed for manual VIP import testing."""

import argparse
import hmac
import json
import re
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

FEED_PATH = "/api/get_shared_vip_list"
PLAYER_ID = re.compile(r"^(?:\d{17}|[0-9a-fA-F]{32})$")


def build_feed(config):
    if not isinstance(config, dict) or not isinstance(config.get("players"), list):
        raise TypeError("players must be a list")
    if not isinstance(config.get("list_name"), str):
        raise TypeError("list_name must be a string")
    if not isinstance(config.get("sharing_enabled"), bool):
        raise TypeError("sharing_enabled must be a boolean")
    key = config.get("share_key")
    if not isinstance(key, str) or len(key) < 32:
        raise ValueError("share_key must have at least 32 characters")

    now = datetime.now(UTC)
    seen = set()
    records = []
    for player in config["players"]:
        if not isinstance(player, dict):
            raise TypeError("each player must be an object")
        player_id = player.get("player_id")
        if not isinstance(player_id, str) or not PLAYER_ID.fullmatch(player_id):
            raise ValueError("invalid player_id")
        if player_id in seen:
            raise ValueError("duplicate player_id")
        seen.add(player_id)
        if not isinstance(player.get("enabled"), bool):
            raise TypeError("enabled must be a boolean")
        description = player.get("description")
        if description is not None and (
            not isinstance(description, str) or len(description) > 255
        ):
            raise ValueError("invalid description")
        expiry = player.get("expires_at")
        if expiry is not None:
            if not isinstance(expiry, str):
                raise ValueError("expires_at must be an ISO 8601 string or null")
            parsed = datetime.fromisoformat(expiry)
            if parsed.tzinfo is None:
                raise ValueError("expires_at needs a timezone")
            if parsed <= now:
                continue
        if player["enabled"]:
            records.append(
                {
                    "player_id": player_id,
                    "description": description,
                    "expires_at": expiry,
                }
            )
    return (
        key,
        config["sharing_enabled"],
        {
            "failed": False,
            "result": {
                "schema_version": 1,
                "list": {"name": config["list_name"]},
                "records": records,
            },
        },
    )


def handler_for(config_path):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != FEED_PATH:
                self.respond(404, {"error": "Not found"})
                return
            try:
                key, sharing_enabled, feed = build_feed(
                    json.loads(config_path.read_text())
                )
            except (OSError, ValueError, TypeError) as exc:
                self.log_error("Invalid test feed configuration: %s", exc)
                self.respond(503, {"error": "Invalid feed configuration"})
                return
            scheme, _, token = self.headers.get("Authorization", "").partition(" ")
            if (
                not sharing_enabled
                or scheme.lower() != "bearer"
                or not hmac.compare_digest(token, key)
            ):
                self.respond(401, {"error": "Invalid share credential"})
                return
            self.respond(200, feed)

        def respond(self, status, body):
            encoded = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), handler_for(args.config))
    print(f"VIP test feed listening on {args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
