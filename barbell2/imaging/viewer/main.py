import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel


def main():
    app = QApplication(sys.argv)
    label = QLabel('Hello, world')
    label.setAlignment(Qt.AlignCenter)
    label.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
