from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget

class ConfigTab(QWidget):
    def __init__(self, config):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Configuration actuelle :"))
        layout.addWidget(QLabel(f"Rafraîchissement: {config['refresh_interval']}s"))
        layout.addWidget(QLabel(f"Thème: {config['theme']}"))
        layout.addWidget(QLabel("Programmes exclus:"))
        exclusion_list = QListWidget()
        for prog in config["exclude_programs"]:
            exclusion_list.addItem(prog)
        layout.addWidget(exclusion_list)
        self.setLayout(layout)