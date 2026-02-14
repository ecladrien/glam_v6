from ..config.manager import Config
from PySide6.QtWidgets import QLineEdit, QPushButton
import logging

logger = logging.getLogger(__name__)

class SetupPageManager:
    def __init__(self, main_window, config: Config):
        self.main_window = main_window
        self.config = config
        self.ui = main_window.ui
        self._connect_buttons()
        self.load_config_to_fields()

    def load_config_to_fields(self):
        self.ui.width_screen_line_edit.setText(str(self.config.display.screen_width))
        self.ui.height_screen_line_edit.setText(str(self.config.display.screen_height))
        self.ui.adress_ip_line_edit.setText(str(getattr(self.config.network, 'device_ip', '')))
        self.ui.adress_ip_cam_line_edit.setText(str(getattr(self.config.network, 'camera_ip', '')))
        self.ui.adress_ip_artnet_line_edit.setText(str(getattr(self.config.network, 'artnet_network', '')))

    def save_fields_to_config(self):
        try:
            self.config.display.screen_width = int(self.ui.width_screen_line_edit.text())
            self.config.display.screen_height = int(self.ui.height_screen_line_edit.text())
            self.config.network.device_ip = self.ui.adress_ip_line_edit.text()
            self.config.network.camera_ip = self.ui.adress_ip_cam_line_edit.text()
            self.config.network.artnet_network = self.ui.adress_ip_artnet_line_edit.text()
            self.config.save()
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text('Configuration sauvegardée.')
        except Exception as e:
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text(f'Erreur lors de la sauvegarde: {e}')
            logger.exception("Erreur lors de la sauvegarde de la configuration: %s", e)

    def reset_to_default(self):
        default_config = Config()
        self.config.display.screen_width = default_config.display.screen_width
        self.config.display.screen_height = default_config.display.screen_height
        self.config.network.device_ip = default_config.network.device_ip
        self.config.network.camera_ip = default_config.network.camera_ip
        self.config.network.artnet_network = default_config.network.artnet_network
        self.load_config_to_fields()
        if hasattr(self.main_window, 'set_log_text'):
            self.main_window.set_log_text('Valeurs par défaut restaurées (non sauvegardées).')
        

    def _connect_buttons(self):
        self.ui.save_setup_button.clicked.connect(self.save_fields_to_config)
        self.ui.reset_setup_button.clicked.connect(self.reset_to_default)
