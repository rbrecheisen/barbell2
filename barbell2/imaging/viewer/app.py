import sys

from PySide6 import QtWidgets


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Hello, world!')
        label = QtWidgets.QLabel('Bla')
        label.setMargin(10)
        self.setCentralWidget(label)
        self.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec()
