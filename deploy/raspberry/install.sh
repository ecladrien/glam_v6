#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"

echo "[GLAM] Installation Raspberry Pi - dossier projet: ${PROJECT_DIR}"

sudo apt-get update
sudo apt-get install -y \
  python3 python3-venv python3-pip \
  ffmpeg libglib2.0-0 libgl1 libegl1 libxkbcommon-x11-0 libxcb-cursor0 \
  libdbus-1-3 libnss3 libxcomposite1 libxdamage1 libxrandr2 libxi6 libxtst6 \
  libasound2 libatk1.0-0 libcups2 libx11-xcb1 \
  qlcplus

if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

"${VENV_DIR}/bin/pip" install --upgrade pip setuptools wheel

# Dépendances Python principales (hors OpenCV pour gérer le fallback ARM)
"${VENV_DIR}/bin/pip" install \
  "pytest>=7.0" \
  "pydantic>=2.0" \
  "PySide6>=6.10" \
  "nanpy>=0.9.6" \
  onvif_zeep==0.2.12

echo "[GLAM] Installation OpenCV (tentative wheel standard puis fallback headless)"
if ! "${VENV_DIR}/bin/pip" install opencv-python==4.13.0.92; then
  echo "[GLAM] opencv-python indisponible sur cette archi, fallback vers opencv-python-headless"
  "${VENV_DIR}/bin/pip" install opencv-python-headless
fi

echo "[GLAM] Permissions série Arduino"
sudo usermod -aG dialout "$USER" || true

echo "[GLAM] Installation terminée"
echo "- Reconnecte-toi pour appliquer le groupe dialout (ou redémarre la session)."
echo "- Lancement manuel: ${PROJECT_DIR}/deploy/raspberry/run_glam.sh"
