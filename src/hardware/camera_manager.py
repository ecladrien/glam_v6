import cv2
import time
from typing import Optional
from onvif import ONVIFCamera

from ..config.manager import Config


class ReolinkCamera:
    """Camera helper that can load connection data from the app config.

    If any of `ip`, `rtsp_user`, `rtsp_password` or `onvif_port` is not
    provided, the value will be read from `Config.load_default()`.
    """

    def __init__(
        self,
        ip: Optional[str] = None,
        rtsp_user: Optional[str] = None,
        rtsp_password: Optional[str] = None,
        rtsp_stream: Optional[str] = None,
        onvif_port: Optional[int] = None,
    ):
        # Load defaults from config when values are missing
        cfg = Config.load_default()

        if ip is None:
            ip = cfg.network.camera_ip
        if rtsp_user is None:
            rtsp_user = cfg.camera.rtsp_user
        if rtsp_password is None:
            rtsp_password = cfg.camera.rtsp_password
        if rtsp_stream is None:
            rtsp_stream = cfg.camera.rtsp_stream
        if onvif_port is None:
            onvif_port = cfg.camera.onvif_port

        self.ip = ip
        self.rtsp_url = f"rtsp://{rtsp_user}:{rtsp_password}@{ip}{rtsp_stream}"

        # --- RTSP ---
        self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)

        if not self.cap.isOpened():
            raise RuntimeError("Impossible d’ouvrir le flux RTSP")

        # --- ONVIF ---
        self.cam = ONVIFCamera(ip, onvif_port, rtsp_user, rtsp_password)
        self.media = self.cam.create_media_service()
        self.ptz = self.cam.create_ptz_service()
        self.profile = self.media.GetProfiles()[0]

        self.zoom_request = self.ptz.create_type("ContinuousMove")
        self.zoom_request.ProfileToken = self.profile.token
        self.zoom_request.Velocity = {"Zoom": {"x": 0}}

    # -------------------------------
    # VIDEO
    # -------------------------------
    def show(self, window_name="Reolink RLC-811A"):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Flux vidéo perdu")
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
    # ZOOM
    # -------------------------------
    def zoom(self, speed=0.5, duration=1.0):
        self.zoom_request.Velocity["Zoom"]["x"] = speed
        self.ptz.ContinuousMove(self.zoom_request)
        time.sleep(duration)
        self.stop_zoom()

    def zoom_in(self, speed=0.5, duration=0.8):
        self.zoom(speed, duration)

    def zoom_out(self, speed=0.5, duration=0.8):
        self.zoom(-speed, duration)

    def stop_zoom(self):
        self.ptz.Stop({"ProfileToken": self.profile.token})

    def zoom_reset(self):
        """Recul complet du zoom (position connue)"""
        self.zoom(-1.0, 3.0)

    # -------------------------------
    # CLEANUP
    # -------------------------------
    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
