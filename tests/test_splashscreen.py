import os
import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app import _create_splash
from src.config.manager import Config


def _run_splash(duration_ms: int = 1500) -> None:
    app = QApplication.instance() or QApplication([])
    config = Config.load_default()
    splash = _create_splash(config)
    splash.show()

    QTimer.singleShot(duration_ms, splash.close)
    QTimer.singleShot(duration_ms, app.quit)
    app.exec()


def test_splashscreen_display() -> None:
    if os.environ.get("GLAM_SHOW_SPLASH", "0") != "1":
        return
    _run_splash()


if __name__ == "__main__":
    _run_splash()
