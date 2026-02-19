import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow
from .utils.logging_config import setup_logging
from .config.manager import Config
from .gui.main_window import MainWindow
from .gui.ui_Splash_screen import Ui_SplashScreen


class SplashScreenWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)


def _create_splash(config: Config) -> SplashScreenWindow:
    project_root = Path(__file__).resolve().parents[1]
    splash_candidates = [
        project_root / "ressources" / "img" / "splashscreen.png",
        Path(config.paths.default_img),
    ]

    pixmap = QPixmap()
    for candidate in splash_candidates:
        if candidate.exists() and pixmap.load(str(candidate)):
            break

    splash = SplashScreenWindow()
    if not pixmap.isNull():
        splash.ui.splashscreen_img.setScaledContents(True)
        splash.ui.splashscreen_img.setPixmap(pixmap)
    splash.ui.please_wait_label.setText("Démarrage de GLAM...")
    return splash


def main() -> None:
    logger = setup_logging("glam.app")
    try:
        # Initialiser l'application Qt
        app = QApplication(sys.argv)

        config = Config.load_default()
        logger.info("GLAM starting")

        splash = _create_splash(config)
        splash.show()
        app.processEvents()
        splash.ui.please_wait_label.setText("Chargement de la fenêtre principale...")
        app.processEvents()

        # Créer la fenêtre principale en lui passant la config si possible
        try:
            window = MainWindow(config)
        except TypeError:
            window = MainWindow()

        window.show()
        splash.close()

        logger.info("GUI window displayed")
        window.set_log_text("GLAM started successfully")

        # Lancer la boucle d'événements Qt et retourner le code de sortie
        exit_code = app.exec()
        logger.info(f"Qt event loop exited with code {exit_code}")
        sys.exit(exit_code)
    except Exception:
        logger.exception("Unhandled exception during application startup")
        sys.exit(1)


if __name__ == "__main__":
    main()
