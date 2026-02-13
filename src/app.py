import sys
from PySide6.QtWidgets import QApplication
from utils.logging_config import setup_logging
from config.manager import Config
from gui.main_window import MainWindow


def main() -> None:
    logger = setup_logging("glam.app")
    try:
        config = Config.load_default()
        logger.info("GLAM starting")
        logger.info(f"Config loaded: screen_width={config.screen_width} screen_height={config.screen_height}")

        # Initialiser l'application Qt
        app = QApplication(sys.argv)

        # Créer la fenêtre principale en lui passant la config si possible
        try:
            window = MainWindow(config)
        except TypeError:
            window = MainWindow()

        window.show()

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
