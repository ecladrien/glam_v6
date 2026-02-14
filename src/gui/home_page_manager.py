from ..config.manager import Config
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QProcess
from pathlib import Path
import sys
import os
from PySide6.QtGui import QPixmap

class HomePageManager:
    def __init__(self, main_window, config: Config):
        self.main_window = main_window
        self.config = config
        self.ui = main_window.ui
        self._connect_buttons()
        # Afficher la home_page
        try:
            self.ui.main_frame.setCurrentWidget(self.ui.home_page)

            head_path = Path(getattr(self.config, "head_img", ""))
            default_path = Path(getattr(self.config, "default_img", ""))

            chosen = None
            if head_path.exists():
                chosen = head_path
            elif default_path.exists():
                chosen = default_path

            if chosen is None:
                if hasattr(self.main_window, 'set_log_text'):
                    self.main_window.set_log_text("Aucune image de fond disponible (head_img ou default_img) - vérifier la config")
                return

            pix = QPixmap(str(chosen))
            if pix.isNull():
                if hasattr(self.main_window, 'set_log_text'):
                    self.main_window.set_log_text("Impossible de charger l'image de fond")
                return

            label = self.ui.background_image

            label.setScaledContents(False)
            w = max(1, (label.width()*2.5))
            h = max(1, (label.height()*2.5))
            scaled = pix.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(scaled)
        except Exception as e:
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text(f"Erreur affichage home_page: {e}")


    def _connect_buttons(self):
        self.ui.restart_button.clicked.connect(self._restart_button_clicked)
        self.ui.shutdown_button.clicked.connect(self.shutdown_button_clicked)

    def _restart_button_clicked(self):
        # Sauvegarder la config si un gestionnaire est disponible, sinon sauvegarder la config brute
        try:
            if hasattr(self.main_window, 'setup_page_manager') and hasattr(self.main_window.setup_page_manager, 'save_fields_to_config'):
                self.main_window.setup_page_manager.save_fields_to_config()
            else:
                # Persister la config actuelle
                try:
                    self.config.save()
                except Exception:
                    pass
        except Exception as e:
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text(f"Erreur lors de la sauvegarde avant restart: {e}")

        # Redémarrer l'application
        try:
            QApplication.quit()
            QProcess.startDetached(sys.executable, sys.argv)
        except Exception as e:
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text(f"Erreur lors du redémarrage: {e}")

    def shutdown_button_clicked(self):
        # Sauvegarder la config si possible
        try:
            if hasattr(self.main_window, 'setup_page_manager') and hasattr(self.main_window.setup_page_manager, 'save_fields_to_config'):
                self.main_window.setup_page_manager.save_fields_to_config()
            else:
                try:
                    self.config.save()
                except Exception:
                    pass
        except Exception:
            pass

        # Tenter un arrêt propre si la plateforme le permet (peut nécessiter des privilèges)
        try:
            self.main_window.set_log_text('Tentative d\'arrêt du système...')   
            """
            if sys.platform.startswith("linux"):
                os.system("shutdown -h now")
            elif sys.platform == "darwin":
                # macOS shutdown via AppleScript (may prompt for privileges)
                os.system("osascript -e 'tell app \"System Events\" to shut down'")
            else:
                if hasattr(self.main_window, 'set_log_text'):
                    self.main_window.set_log_text('Shutdown non supporté sur ce système.')"""
        except Exception as e:
            if hasattr(self.main_window, 'set_log_text'):
                self.main_window.set_log_text(f'Erreur shutdown: {e}')