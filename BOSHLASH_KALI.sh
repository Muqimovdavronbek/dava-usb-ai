#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' 'Python 3 topilmadi. Kali Linux odatda Python 3 bilan keladi.'
  exit 1
fi
exec python3 "$ROOT/tools/start_linux.py" "$@"
