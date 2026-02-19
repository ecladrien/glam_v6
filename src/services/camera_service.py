from __future__ import annotations
from typing import List
import socket
import logging

logger = logging.getLogger(__name__)


class CameraService:
    """Service pour la découverte des caméras via test de port RTSP (554).

    Cette classe encapsule la logique réseau (sockets) pour permettre
    des tests unitaires et séparer la logique métier de l'UI.
    """

    def __init__(self, timeout: float = 0.4, max_results: int = 8):
        self.timeout = float(timeout)
        self.max_results = int(max_results)

    def _check_rtsp(self, ip: str, timeout: float | None = None) -> bool:
        t = self.timeout if timeout is None else timeout
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(t)
        try:
            s.connect((ip, 554))
            return True
        except Exception:
            return False
        finally:
            try:
                s.close()
            except Exception:
                logger.debug('socket close failed for %s', ip)

    def scan_subnet_for_rtsp(self, base_ip: str, limit: int = 254, timeout: float | None = None) -> List[str]:
        found: List[str] = []
        try:
            parts = base_ip.split('.')
            if len(parts) < 4:
                return found
            prefix = '.'.join(parts[:3]) + '.'
            for i in range(1, limit):
                ip = f"{prefix}{i}"
                try:
                    if self._check_rtsp(ip, timeout=timeout):
                        found.append(ip)
                except Exception:
                    logger.debug('connect to %s failed during scan', ip)
                if len(found) >= self.max_results:
                    break
        except Exception:
            logger.exception('Error scanning subnet')
        return found

    def discover_cameras(self, cfg_ip: str | None) -> List[str]:
        """Discover cameras preferring the configured IP, otherwise scanning subnet."""
        ips: List[str] = []
        try:
            if cfg_ip:
                try:
                    if self._check_rtsp(cfg_ip):
                        ips.append(cfg_ip)
                except Exception:
                    logger.debug('connect to configured camera %s failed', cfg_ip)

            if not ips and cfg_ip:
                ips.extend(self.scan_subnet_for_rtsp(cfg_ip))
        except Exception:
            logger.exception('Error during camera discovery')
        return ips
