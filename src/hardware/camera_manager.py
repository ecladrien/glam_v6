import cv2
import time
from typing import Optional
from ..config.manager import Config
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

try:
    from onvif import ONVIFCamera  # optional dependency
except Exception:  # pragma: no cover - optional
    ONVIFCamera = None


class CameraError(RuntimeError):
    pass


class ReolinkCamera:
    """Camera helper that can load connection data from the app config.

    Behaviour and API:
    - Constructor accepts the same optional params as before (ip, rtsp_user, ...)
      but will fall back to `Config.load_default()` when values are missing.
    - Methods: `connect_rtsp()`, `connect_onvif()`, `is_open()`, `read_frame()`,
      `show(window_name)` and `release()`.
    - ONVIF features are optional and only available when `onvif` package is installed.
    """

    def __init__(
        self,
        ip: Optional[str] = None,
        rtsp_user: Optional[str] = None,
        rtsp_password: Optional[str] = None,
        rtsp_stream: Optional[str] = None,
        onvif_port: Optional[int] = None,
        cfg: Optional[Config] = None,
    ) -> None:
        cfg = cfg or Config.load_default()

        self.ip = ip or cfg.network.camera_ip
        self.rtsp_user = rtsp_user or cfg.camera.rtsp_user
        pw = rtsp_password if rtsp_password is not None else cfg.camera.rtsp_password
        # Unwrap SecretStr if present
        self.rtsp_password = pw.get_secret_value() if hasattr(pw, "get_secret_value") else pw
        self.rtsp_stream = rtsp_stream or cfg.camera.rtsp_stream
        self.onvif_port = onvif_port or cfg.camera.onvif_port

        self.rtsp_url = f"rtsp://{self.rtsp_user}:{self.rtsp_password}@{self.ip}{self.rtsp_stream}"

        self.cap: Optional[cv2.VideoCapture] = None
        self.cam = None
        self.media = None
        self.ptz = None
        self.profile = None

        # attempt to connect RTSP lazily
        try:
            self.connect_rtsp()
        except Exception:
            logger.debug("Initial RTSP connect failed; will try on first read")

        # attempt ONVIF only if available
        if ONVIFCamera is not None:
            try:
                self.connect_onvif()
            except Exception:
                logger.debug("ONVIF connection failed or not configured")

    # -------------------------------
    # CONNECTIONS
    # -------------------------------
    def connect_rtsp(self, backend=cv2.CAP_FFMPEG, timeout_sec: float = 5.0) -> None:
        """Open the RTSP VideoCapture. Raises CameraError on failure."""
        if self.cap and getattr(self.cap, "isOpened", lambda: False)():
            return

        self.cap = cv2.VideoCapture(self.rtsp_url, backend)
        start = time.time()
        # allow small time to initialize
        while time.time() - start < timeout_sec:
            if self.cap.isOpened():
                return
            time.sleep(0.1)

        raise CameraError(f"Impossible d'ouvrir le flux RTSP: {self.rtsp_url}")

    def connect_onvif(self) -> None:
        """Initialize ONVIF services when supported."""
        if ONVIFCamera is None:
            raise CameraError("onvif package not installed")

        if self.cam is not None:
            return

        self.cam = ONVIFCamera(self.ip, self.onvif_port, self.rtsp_user, self.rtsp_password)
        self.media = self.cam.create_media_service()
        self.ptz = self.cam.create_ptz_service()
        profiles = self.media.GetProfiles()
        if not profiles:
            raise CameraError("No ONVIF profiles available")
        self.profile = profiles[0]

    # -------------------------------
    # VIDEO
    # -------------------------------
    def is_open(self) -> bool:
        return bool(self.cap and self.cap.isOpened())

    def read_frame(self):
        """Read a single frame from RTSP. Returns (ret, frame)."""
        if not self.cap or not self.cap.isOpened():
            try:
                self.connect_rtsp()
            except Exception as exc:
                logger.exception("RTSP connect failed on read")
                return False, None

        return self.cap.read()

    def show(self, window_name: str = "Reolink Camera") -> None:
        """Show continuous preview window. Keyboard controls: q quit, + zoom in, - zoom out, r reset.
        ONVIF zoom commands are no-ops if ONVIF not available."""
        while True:
            ret, frame = self.read_frame()
            if not ret:
                logger.debug("Video stream lost or frame not read")
                break

            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("+"):
                self.zoom_in()
            elif key == ord("-"):
                self.zoom_out()
            elif key == ord("r"):
                self.zoom_reset()

        self.release()

    # -------------------------------
    # ZOOM (ONVIF)
    # -------------------------------
    def _ensure_ptz(self):
        if not self.ptz or not self.profile:
            self.connect_onvif()

    def zoom(self, speed: float = 0.5, duration: float = 1.0) -> None:
        if ONVIFCamera is None:
            logger.debug("ONVIF not available; zoom ignored")
            return

        try:
            self._ensure_ptz()
            req = self.ptz.create_type("ContinuousMove")
            req.ProfileToken = self.profile.token
            req.Velocity = {"Zoom": {"x": float(speed)}}
            self.ptz.ContinuousMove(req)
            time.sleep(duration)
            self.ptz.Stop({"ProfileToken": self.profile.token})
        except Exception:
            logger.exception("ONVIF zoom failed")

    def zoom_in(self, speed: float = 0.5, duration: float = 0.8) -> None:
        self.zoom(speed, duration)

    def zoom_out(self, speed: float = 0.5, duration: float = 0.8) -> None:
        self.zoom(-speed, duration)

    def zoom_reset(self) -> None:
        self.zoom(-1.0, 3.0)

    # -------------------------------
    # CLEANUP
    # -------------------------------
    def release(self) -> None:
        try:
            if self.cap:
                self.cap.release()
        except Exception:
            logger.exception("Error releasing VideoCapture")
        try:
            cv2.destroyAllWindows()
        except Exception as e:
            logger.debug("Error destroying OpenCV windows: %s", e)
