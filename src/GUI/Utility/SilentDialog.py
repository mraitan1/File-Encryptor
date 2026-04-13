from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from src.GUI.Utility.ResourcePath import resource_path

# DAMN WINDOWS NOISES
class SilentDialog(QDialog):
    def __init__(self, title: str, text: str, parent=None, icon_path = None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        # REMOVE WINDOWS BULLSHIT
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        self.setWindowIcon(QIcon(resource_path(icon_path)))

        layout = QVBoxLayout()
        label = QLabel(f"<span style='color:#ff2e88; font-size:15px;'>{text}</span>")
        label.setWordWrap(True)
        layout.addWidget(label)

        ok = QPushButton("OK")
        ok.setStyleSheet("""
            background-color: #ff2e88;
            color: black;
            font-weight: bold;
            border-radius: 5px;
            padding: 6px;
        """)
        ok.clicked.connect(self.accept) # type: ignore
        layout.addWidget(ok, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)


def show_info(parent, title, text):
    dlg = SilentDialog(title, text, parent, icon_path = "icons/check.png")
    dlg.exec()


def show_error(parent, title, text):
    dlg = SilentDialog(title, text, parent, icon_path = "icons/Skull_edit.png")
    dlg.exec()
