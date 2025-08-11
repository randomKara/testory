#!/usr/bin/env bash
set -euo pipefail

# Simple sanity tests using curl

echo "[1/5] Check Hydra public"
curl -sSf http://localhost:4444/health/ready >/dev/null

echo "[2/5] Check Kratos public"
curl -sSf http://localhost:4433/health/ready >/dev/null

echo "[3/5] Create Kratos identity via admin API"
IDENTITY_JSON='{"schema_id":"default","traits":{"email":"demo@example.com"}}'
curl -sSf -X POST http://localhost:4434/admin/identities -H 'content-type: application/json' -d "$IDENTITY_JSON" >/dev/null || true

echo "[4/5] Start OAuth2 authorization code flow"
AUTH_URL="http://localhost:4444/oauth2/auth?client_id=flask-app&response_type=code&scope=openid&redirect_uri=http://localhost:5000/callback&state=xyz"
echo "Open the following URL in a browser to complete manual login (demo):"
echo "$AUTH_URL"

echo "[5/5] Query Flask public root"
curl -sSf http://localhost:5000/ | head -n 5

echo "Done. Use the printed AUTH_URL to finish the flow manually in browser for now."


