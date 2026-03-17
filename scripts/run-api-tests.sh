#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=./api-common.sh
source "${SCRIPT_DIR}/api-common.sh"

load_repo_env
ensure_api_venv
activate_api_venv
install_api_requirements_if_needed

cd "$(api_dir)"
python -m pytest
