#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=./api-common.sh
source "${SCRIPT_DIR}/api-common.sh"

ensure_api_venv
activate_api_venv

python -m pip install -r "$(api_dir)/requirements.txt"
