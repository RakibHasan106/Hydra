import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hail Hydra!")
        self.setGeometry(1300,200,400,400)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        #Adding Buttons
        

def main():
    app = QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()