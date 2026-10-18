#!/usr/bin/env bash
# Serve the Coral docs site locally.
# Usage: ./serve.sh [port]   (default port 8000)
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-8000}"
echo "Serving $(pwd) at http://localhost:${PORT}/"
exec python3 -m http.server "${PORT}"
