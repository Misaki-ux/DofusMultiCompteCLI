# logic/app_config.py

class AppConfig:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppConfig, cls).__new__(cls, *args, **kwargs)
            cls._instance.config = {}
        return cls._instance

    def get_config(self):
        return self.config

    def set_config(self, new_config):
        self.config = new_config

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value

    def get_window_position(self, hwnd):
        """Get the saved position for a window handle."""
        window_positions = self.config.get("window_positions", {})
        return window_positions.get(str(hwnd))

    def set_window_position(self, hwnd, rect):
        """Save the position for a window handle."""
        window_positions = self.config.get("window_positions", {})
        window_positions[str(hwnd)] = list(rect)  # Convert tuple to list
        self.config["window_positions"] = window_positions
        self.save()

# Global instance
app_config = AppConfig()
