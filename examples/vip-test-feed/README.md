# Editable VIP partner test feed

This isolated test server speaks the same read-only feed protocol as VIP list
sharing. It reads `config.json` on **every request**, so changing the player
list does not require a restart. An invalid config returns HTTP 503 rather
than an empty list. The server cannot change CRCON directly.

## Start

From the repository root:

```bash
cd examples/vip-test-feed
cp config.example.json config.json
chmod 600 config.json
python3 - <<'PY'
import json
import secrets
from pathlib import Path

path = Path('config.json')
data = json.loads(path.read_text())
data['share_key'] = 'vls_' + secrets.token_urlsafe(32)
path.write_text(json.dumps(data, indent=2) + '\n')
PY
docker compose -f docker-compose.test-feed.yaml up -d
```

Replace the example ID with a real test player's Steam64 ID (17 digits) or
HLL Vietnam network ID (32 hexadecimal characters). Keep `enabled` set to
`false` until you are ready to test activation. The example config is ignored
by Git; never commit the actual `config.json` or paste its `share_key` into a
chat. The container exposes port 8765 on the server's loopback interface.

Check locally with a hidden key prompt:

```bash
read -r -s -p 'Test feed key: ' test_feed_key; echo
curl -sS -o /dev/null -w 'HTTP %{http_code}\n' \
  -H "Authorization: Bearer $test_feed_key" \
  http://127.0.0.1:8765/api/get_shared_vip_list
unset test_feed_key
```

## Make it reachable by the CRCON importer

Give the feed its own public DNS name, such as `vip-test.example.org`. Configure
your HTTPS reverse proxy to forward requests to the test server on port 8765,
preserve the `Authorization` header, and serve a valid certificate. The import
URL must be exactly `https://vip-test.example.org/api/get_shared_vip_list`
on port 443, without a redirect, query string, or HTTP authentication at the
proxy. The hostname must resolve only to public addresses from the CRCON
backend. If the proxy runs on another host, replace the loopback bind address
in `docker-compose.test-feed.yaml` with a reachable server address and restrict access to the
proxy with a firewall.

Open **Import partner list** in CRCON, enter that URL and the `share_key` from
your private config, and keep **Require approval** enabled for the first test.
No separate CRCON account is needed on the test feed.

## Try the state changes

Edit `config.json` and use **Synchronize now** after each change:

1. Set the real test player's `enabled` to `true`: the record appears pending.
2. Approve the record in CRCON: it becomes active and the gameserver VIP sync
   should apply it. Check the gameserver status in the VIP Lists page.
3. Set `expires_at` to a future ISO 8601 timestamp such as
   `2026-10-01T12:00:00+00:00`: the expiry updates on sync.
4. Set `enabled` to `false` or remove the player: the imported record becomes
   inactive on sync. Another active local list can still grant that player VIP.
5. Turn `sharing_enabled` off: the feed returns 401 and CRCON keeps its last
   imported records rather than treating the failure as an empty list.

An expired timestamp also removes the player from the feed. To stop the test
server, run `docker compose -f docker-compose.test-feed.yaml down` from this directory.
