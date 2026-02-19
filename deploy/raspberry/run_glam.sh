#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_PYTHON="${PROJECT_DIR}/.venv/bin/python"

cd "${PROJECT_DIR}"

if [[ ! -x "${VENV_PYTHON}" ]]; then
  echo "[GLAM] Environnement Python introuvable: ${VENV_PYTHON}"
  echo "[GLAM] Lance d'abord deploy/raspberry/install.sh"
  exit 1
fi

exec "${VENV_PYTHON}" -m src.app
