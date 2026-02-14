from ..config.manager import Config



class MeasurementPageManager:
    def __init__(self, main_window, config: Config):
        self.main_window = main_window
        self.config = config
        self.ui = main_window.ui