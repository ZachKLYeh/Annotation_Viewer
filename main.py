import sys
from pyqt import MainWindow
from PyQt5 import QtWidgets

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    app.exec()

