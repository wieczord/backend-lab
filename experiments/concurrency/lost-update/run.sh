#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v uv >/dev/null || { echo "Missing required command: uv" >&2; exit 127; }
command -v docker >/dev/null || { echo "Missing required command: docker" >&2; exit 127; }

cleanup() {
    local status=$?
    trap - EXIT
    docker compose down -v || { if [ "$status" -eq 0 ]; then status=1; fi; }
    exit "$status"
}

uv sync
trap cleanup EXIT
docker compose up -d --wait --wait-timeout 60
uv run pytest "$@"
