import sys
from PyQt6.QtWidgets import QApplication
from src.GUI.EncryptorGUI import EncryptorGUI

def main():
    app = QApplication(sys.argv)
    window = EncryptorGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
