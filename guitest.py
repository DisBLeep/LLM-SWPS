import sys
from PyQt5.QtWidgets import QApplication, QWidget

def test():
    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(250, 150)
    w.setWindowTitle('Simple Test')
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()