#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../apps/api"

if [ ! -d .venv ]; then
  python -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

if ! python -c "import pytest" >/dev/null 2>&1; then
  python -m pip install -r requirements.txt
fi

python -m pytest
