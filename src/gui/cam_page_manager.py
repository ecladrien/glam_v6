from __future__ import annotations

from ..config.manager import Config
import logging
from typing import List
import threading
from pathlib import Path

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QTimer

from ..services.camera_service import CameraService

logger = logging.getLogger(__name__)


class CamPageManager:
    """Manage the camera page: search network for cameras and add buttons.

    When the user clicks the `search_cam_button`, a short network scan is
    performed (checks for open RTSP port 554). For each host found a button
    is created inside the UI layout `horizontalLayout_15` (the grid area).
    Clicking a discovered-camera button will set `config.network.camera_ip`
    to that IP and persist the config.
    """

    def __init__(self, main_window, config: Config):
        self.main_window = main_window
        self.config = config
        self.ui = main_window.ui
        self.camera_service = CameraService()

        try:
            self.ui.search_cam_button.clicked.connect(self._on_search_clicked)
        except Exception:
            logger.debug("search_cam_button not present or not connectable")

    # -------------------------
    # UI helpers
    # -------------------------
    def _add_camera_button(self, ip: str, label: str | None = None) -> None:
        try:
            layout = getattr(self.ui, "horizontalLayout_15", None)
            if layout is None:
                logger.debug("camera layout not found")
                return

            # Avoid duplicate buttons for same IP
            for i in range(layout.count()):
                w = layout.itemAt(i).widget()
                if w is not None and getattr(w, "property", lambda x: None)("camera_ip") == ip:
                    return

            btn = QPushButton(label or f"Camera {ip}")
            btn.setProperty("camera_ip", ip)

            def _on_click(checked=False, ip=ip):
                try:
                    self.config.network.camera_ip = ip
                    self.config.save()
                    if hasattr(self.main_window, "set_log_text"):
                        self.main_window.set_log_text(f"Camera sélectionnée: {ip}")
                except Exception:
                    logger.exception("Failed to set selected camera ip")

            btn.clicked.connect(_on_click)
            layout.addWidget(btn)
        except Exception:
            logger.exception("Failed to add camera button to UI")

    # -------------------------
    # Network scan
    # -------------------------
    def _scan_subnet_for_rtsp(self, base_ip: str, limit: int = 254, timeout: float = 0.4) -> List[str]:
        # Delegate to CameraService
        return self.camera_service.scan_subnet_for_rtsp(base_ip, limit=limit, timeout=timeout)

    def _on_search_clicked(self) -> None:
        # Run scan in background thread and add buttons on the main thread
        def _worker():
            ips: List[str] = []
            # First check configured camera ip
            try:
                cfg_ip = getattr(self.config.network, "camera_ip", None)
                ips = self.camera_service.discover_cameras(cfg_ip)
            except Exception:
                logger.exception("Error during camera discovery")

            # Schedule UI updates on main thread
            for ip in ips:
                QTimer.singleShot(0, lambda ip=ip: self._add_camera_button(ip))

            if not ips and hasattr(self.main_window, "set_log_text"):
                QTimer.singleShot(0, lambda: self.main_window.set_log_text("Aucune caméra trouvée"))

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
