#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v uv >/dev/null || { echo "Missing required command: uv" >&2; exit 127; }

exec uv run pytest "$@"
