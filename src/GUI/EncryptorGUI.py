import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QFileDialog, QHBoxLayout, QCheckBox, QComboBox, QProgressBar, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QFont, QIcon, QFontDatabase, QPixmap, QPainter, QColor
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import Qt, QUrl, QPropertyAnimation, QSize, QEasingCurve, QByteArray

from src.EncryptClient import process_file
from src.GUI.Utility.SilentDialog import show_info, show_error
from src.GUI.Utility.ResourcePath import resource_path

class EncryptorGUI(QWidget):

    def __init__(self):
        super().__init__()

        #  These aren't 'needed', but the yellow warnings were pissing me off
        self.setObjectName("EncryptorGUI")
        self._animations = []
        self._strength_anim = None
        self.sfx_error = None
        self.sfx_complete = None
        self.sfx_click = None
        self.title_label = None
        self.strength_bar = None
        self.delete_box = None
        self.file_label = None
        self.mode_box = None
        self.password_input = None
        self.password_confirm = None
        self.safe_delete_box = None
        self.file_path = None

        self.init_sounds()
        self.init_ui()
        self.apply_punk_theme()
        self.setAcceptDrops(True)

    def init_sounds(self):
        # Click
        self.sfx_click = QSoundEffect()
        self.sfx_click.setSource(QUrl.fromLocalFile(resource_path("sounds/click.wav")))
        self.sfx_click.setVolume(0.2)  # 0.0–1.0

        # Completed
        self.sfx_complete = QSoundEffect()
        self.sfx_complete.setSource(QUrl.fromLocalFile(resource_path("sounds/complete.wav")))
        self.sfx_complete.setVolume(0.2)

        # Error
        self.sfx_error = QSoundEffect()
        self.sfx_error.setSource(QUrl.fromLocalFile(resource_path("sounds/error.wav")))
        self.sfx_error.setVolume(0.1)


    def init_ui(self):

        metal_path = resource_path("fonts/Metal Lord.otf")
        metal_id = QFontDatabase.addApplicationFont(metal_path)
        if metal_id != -1:
            metal_font = QFontDatabase.applicationFontFamilies(metal_id)[0]
        else:
            metal_font = "Arial"

        punk_path = resource_path("fonts/Funkrocker.otf")
        punk_id = QFontDatabase.addApplicationFont(punk_path)
        if punk_id != -1:
            punk_font = QFontDatabase.applicationFontFamilies(punk_id)[0]
        else:
            punk_font = metal_font

        self.setWindowTitle("Anarchy Encryption")
        self.setGeometry(300, 200, 500, 350)
        self.setFont(QFont(metal_font, 11))
        self.setWindowIcon(QIcon(resource_path("icons/icon.png")))

        layout = QVBoxLayout()
        layout.setSpacing(12)

        self.title_label = QLabel("ANARCHY ENCRYPTION")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont(punk_font, 30))
        self.title_label.setStyleSheet("""
            color: #ff2e88;
            text-shadow: 2px 2px #000000;
        """)

        # File selection
        self.file_label = QLabel("Drag & Drop or Select File")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setFont(QFont(metal_font, 14))
        self.file_label.setStyleSheet("""
            color: #77ccff; 
            font-size: 14px;
            font-weight: bold;
        """)
        btn_select = QPushButton("Select File")
        btn_select.setIcon(QIcon(resource_path("icons/Folder_edit.png")))
        btn_select.setIconSize(QSize(24, 24))
        btn_select.clicked.connect(self.play_click) # type: ignore
        btn_select.clicked.connect(self.select_file) # type: ignore

        # Mode selector
        mode_row = QHBoxLayout()
        mode_label = QLabel("Mode:")
        self.mode_box = QComboBox()
        self.mode_box.addItems(["encrypt", "decrypt"])
        mode_row.addWidget(mode_label)
        mode_row.addWidget(self.mode_box)
        self.mode_box.currentTextChanged.connect(self.update_mode_ui)  # type: ignore

        # Password fields
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.textChanged.connect(self.update_password_strength) # type: ignore

        self.password_confirm = QLineEdit()
        self.password_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_confirm.setPlaceholderText("Confirm password")

        # Password strength bar
        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setFixedHeight(8)

        # Delete original toggle
        self.delete_box = QCheckBox("Delete original after encryption")
        self.delete_box.setFont(QFont(metal_font, 14))
        self.delete_box.setStyleSheet("""
            color: #77ccff; 
            font-size: 14px;
            font-weight: bold;
        """)

        # Run button
        btn_run = QPushButton("Run")
        btn_run.setIcon(QIcon("icons/run.png"))
        btn_select.clicked.connect(self.play_click) # type: ignore
        btn_run.clicked.connect(self.run_operation) # type: ignore

        # NEON BABY!!!
        self.add_neon_pulse(self.password_input)
        self.add_neon_pulse(self.password_confirm)
        self.add_neon_pulse(self.mode_box)
        self.add_neon_pulse(self.delete_box)
        self.add_neon_pulse(btn_select)

        # Add to layout
        layout.addWidget(self.title_label)

        layout.addWidget(btn_select)
        layout.addWidget(btn_select)
        layout.addWidget(self.file_label)

        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode:")
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_box, stretch=1)
        layout.addLayout(mode_layout)

        layout.addWidget(self.password_input)
        layout.addWidget(self.strength_bar)
        layout.addWidget(self.password_confirm)
        layout.addWidget(self.delete_box)
        layout.addWidget(btn_run)

        self.setLayout(layout)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            self.file_path = path
            self.file_label.setText(os.path.basename(path))

    def run_operation(self):
        # Checks file path
        if not self.file_path:
            self.play_error()
            show_error(self, "Error", "Please select a file.")
            return

        # Establishes current mode and password
        mode = self.mode_box.currentText()
        password = self.password_input.text()

        if not password:
            self.play_error()
            show_error(self, "Error", "Password cannot be empty.")
            return

        # Confirm password
        if mode == "encrypt":
            if password != self.password_confirm.text():
                self.play_error()
                show_error(self, "Error", "Passwords do not match.")
                return

        try:
            out = process_file(
                mode=mode,
                input_path=self.file_path,
                password=password,
                output_path=None,
                delete_original=self.delete_box.isChecked()
            )

            # Deletes the encrypted file after decryption
            if mode == "decrypt" and self.file_path.endswith(".enc"):
                try:
                    os.remove(self.file_path)
                except Exception as e:
                    self.play_error()
                    print(f"Could not delete encrypted file: {e}")

            self.play_complete()
            show_info(self, "Success", f"Output written to:\n{out}")

        except Exception as e:
            self.play_error()
            show_error(self, "Error", f"Operation failed:\n{e}")

    # Dark Theme
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QLineEdit, QComboBox {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 6px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0060b3;
            }
            QCheckBox {
                spacing: 6px;
            }
            QProgressBar {
                background-color: #333;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #00c853;
                border-radius: 5px;
            }
        """)

    # Punk Theme
    def apply_punk_theme(self):
        self.setStyleSheet(f"""

        EncryptorGUI {{
            background: transparent;
        }}

        QWidget {{
            color: #e0e0e0;
            background: transparent;
        }}

        QLabel {{
            background-color: rgba(44, 44, 44, 180);
            color: #ff2e88;
            border: 2px solid #ff2e88;
            border-radius: 6px;
            padding: 6px;
        }}

        QLineEdit {{
            background-color: rgba(44, 44, 44, 180);
            color: #e3e3e3;
            border: 2px solid #ff2e88;
            border-radius: 6px;
            padding: 6px;
        }}

        QLineEdit:focus {{
            border: 2px solid #ffee32;
        }}

        QComboBox {{
            background-color: rgba(44, 44, 44, 180);
            color: #e3e3e3;
            border: 2px solid #ff2e88;
            border-radius: 6px;
            padding: 6px;
        }}

        QComboBox QAbstractItemView {{
            background-color: #1b1b1b;
            color: #ff2e88;
            selection-background-color: #ff2e88;
        }}

        QPushButton {{
            background-color: rgba(44, 44, 44, 180);
            color: #e3e3e3;
            border: 2px solid #ff2e88;
            border-radius: 6px;
            padding: 6px;
        }}

        QPushButton:hover {{
            background-color: #ffee32;
            color: black;
        }}

        QCheckBox {{
            background-color: rgba(44, 44, 44, 180);
            color: #ff2e88;
            border: 2px solid #ff2e88;
            border-radius: 6px;
            padding: 6px;
        }}

        QProgressBar {{
            background-color: rgba(44, 44, 44, 150);
            border-radius: 4px;
        }}

        QProgressBar::chunk {{
            background-color: #39ff14;
            border-radius: 4px;
        }}
    """)

    # Custom background
    def paintEvent(self, event):
        painter = QPainter(self)
        bg = QPixmap(resource_path("icons/window_background.png"))
        painter.drawPixmap(self.rect(), bg)
        super().paintEvent(event)

    # Drag & Drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        if os.path.isfile(file_path):
            self.file_path = file_path
            self.file_label.setText(os.path.basename(file_path))

    # Password strength bar
    def update_password_strength(self):
        pwd = self.password_input.text()

        strength = 0
        if len(pwd) >= 6: strength += 20
        if len(pwd) >= 10: strength += 20
        if any(c.isdigit() for c in pwd): strength += 20
        if any(c.isupper() for c in pwd): strength += 20
        if any(not c.isalnum() for c in pwd): strength += 20

        self.animate_strength_bar(strength)
        self.color_strength_bar(strength)

    def animate_strength_bar(self, target_value):
        anim = QPropertyAnimation(self.strength_bar, b"value")
        anim.setDuration(300)      # smooth transition
        anim.setStartValue(self.strength_bar.value())
        anim.setEndValue(target_value)
        anim.start()
        self._strength_anim = anim

    def color_strength_bar(self, value):
        if value < 30:
            color = "#e53935"  # red
        elif value < 60:
            color = "#fdd835"  # yellow
        else:
            color = "#00e676"  # green

        self.strength_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #333;
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)

    # Custom sounds
    def play_click(self):
        self.sfx_click.play()

    def play_complete(self):
        self.sfx_complete.play()

    def play_error(self):
        self.sfx_error.play()

    # Hides second password widget during decryption mode, also the progress bar
    def update_mode_ui(self, mode):
        if mode == "encrypt":
            self.password_confirm.show()
            self.strength_bar.show()
        else:
            self.password_confirm.hide()
            self.strength_bar.hide()

    # Neon, cause why not?
    def add_neon_pulse(self, widget):
        effect = QGraphicsDropShadowEffect()
        effect.setOffset(0, 0)
        effect.setBlurRadius(20)
        effect.setColor(QColor("#ff2e88"))
        widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"color")
        anim.setDuration(2000)
        anim.setLoopCount(-1)
        anim.setStartValue(QColor("#ff2e88"))
        #anim.setEndValue(QColor("#39ff14"))
        anim.start()

        self._animations.append(anim)
