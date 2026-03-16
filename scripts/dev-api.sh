#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=./api-common.sh
source "${SCRIPT_DIR}/api-common.sh"

ensure_api_venv
activate_api_venv
install_api_requirements_if_needed

cd "$(api_dir)"
exec python -m uvicorn app.main:app --host "${API_HOST:-0.0.0.0}" --port "${API_PORT:-8000}"
