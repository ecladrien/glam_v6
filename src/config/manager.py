from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import json


class Config(BaseModel):
    data_file: str = Field("data/measurements.csv")
    screen_width: int = Field(1920)
    screen_height: int = Field(1080)
    plan_dir: str = Field("plans")
    default_img: str = Field("img/unicorn.png")
    head_img: str = Field("img/unicorn.png")
    arduino_port: str = Field("/dev/ttyACM0")
    camera_ip: str = Field("192.168.1.188")
    device_ip: str = Field("192.168.1.69")
    artnet_network: str = Field("2.0.0.69")

    @classmethod
    def load_default(cls, path: Optional[str] = None) -> "Config":
        """Load config from file if exists, else return defaults."""
        if path is None:
            path_obj = Path("config/config.json")
        else:
            path_obj = Path(path)

        try:
            if path_obj.exists():
                data = json.loads(path_obj.read_text())
                return cls(**data)
        except Exception:
            # If file corrupt or parsing fails, fall back to defaults
            pass

        return cls()

    def save(self, path: Optional[str] = None) -> None:
        if path is None:
            path_obj = Path("config/config.json")
            path_obj.parent.mkdir(parents=True, exist_ok=True)
        else:
            path_obj = Path(path)
        path_obj.write_text(self.model_dump_json(indent=4))
