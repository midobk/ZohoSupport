#!/usr/bin/env bash

resolve_python_bin() {
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return 0
  fi

  if command -v python >/dev/null 2>&1; then
    echo "python"
    return 0
  fi

  echo "Python 3 is required but neither python3 nor python is available." >&2
  return 1
}

api_repo_root() {
  cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd
}

api_dir() {
  echo "$(api_repo_root)/apps/api"
}

ensure_api_venv() {
  local python_bin
  local target_api_dir

  python_bin="$(resolve_python_bin)"
  target_api_dir="$(api_dir)"

  if [ ! -d "${target_api_dir}/.venv" ]; then
    "${python_bin}" -m venv "${target_api_dir}/.venv"
  fi
}

activate_api_venv() {
  local target_api_dir

  target_api_dir="$(api_dir)"

  # shellcheck disable=SC1091
  source "${target_api_dir}/.venv/bin/activate"
}

install_api_requirements_if_needed() {
  local target_api_dir

  target_api_dir="$(api_dir)"

  if ! python -c "import fastapi, uvicorn" >/dev/null 2>&1; then
    python -m pip install -r "${target_api_dir}/requirements.txt"
  fi
}
