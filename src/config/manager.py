from __future__ import annotations
from pydantic import BaseModel, Field, SecretStr
import os
from typing import List, Optional
from pathlib import Path
import json


PATHCONFIG = Path("data/config.json")

class DisplayConfig(BaseModel):
    screen_width: int = 1920
    screen_height: int = 1080
    fullscreen: bool = False

class HardwareConfig(BaseModel):
    arduino_port: str = "/dev/cu.usbmodem1101" #"/dev/ttyACM0"

class NetworkConfig(BaseModel):
    camera_ip: str = "192.168.1.188"
    device_ip: str = "192.168.1.69"
    artnet_network: str = "2.0.0.69"

class PathsConfig(BaseModel):
    data_file: Path = Path("./data/measurements.csv")
    plan_dir: Path = Path("./ressources/plans")
    default_img: Path = Path("./ressources/img/unicorn.png")
    head_img: Path = Path("./ressources/img/unicorn.png")
    
class CameraConfig(BaseModel):
    rtsp_stream: str = "/h264Preview_01_main"
    onvif_port: int = 8000
    rtsp_user: str = "admin"
    rtsp_password: SecretStr = Field(default_factory=lambda: SecretStr("admin123"))

class QlcConfig(BaseModel):
    qlc_folder_path: Path = Path("./ressources/qlc_files")
    qlc_file_path: Path = Path("./ressources/qlc_files/default.qxw")


class Config(BaseModel):
    display: DisplayConfig = Field(default_factory=DisplayConfig)
    hardware: HardwareConfig = Field(default_factory=HardwareConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    qlc: QlcConfig = Field(default_factory=QlcConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    camera: CameraConfig = Field(default_factory=CameraConfig)

    @classmethod
    def load_default(cls, path: Optional[str] = None) -> "Config":
        """Load config from file if exists, else return defaults."""
        if path is None:
            path_obj = Path(PATHCONFIG)
        else:
            path_obj = Path(path)

        try:
            if path_obj.exists():
                data = json.loads(path_obj.read_text())
                cfg = cls(**data)
                # Allow overriding secret via environment variable
                env_pw = os.getenv("RTSP_PASSWORD")
                if env_pw:
                    cfg.camera.rtsp_password = SecretStr(env_pw)
                return cfg
        except Exception:
            # If file corrupt or parsing fails, fall back to defaults
            pass

        cfg = cls()
        env_pw = os.getenv("RTSP_PASSWORD")
        if env_pw:
            cfg.camera.rtsp_password = SecretStr(env_pw)
        return cfg

    def save(self, path: Optional[str] = None) -> None:
        if path is None:
            path_obj = Path(PATHCONFIG)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
        else:
            path_obj = Path(path)
        # Do not write secrets to disk; exclude password field when saving
        path_obj.write_text(self.model_dump_json(indent=4, exclude={"camera": {"rtsp_password"}}))
