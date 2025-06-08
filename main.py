
import sys
import pages.firstPage as firstPage, pages.secondPage as secondPage, pages.thirdPage as thirdPage
from PyQt5.QtWidgets import (QWidget, 
                             QApplication, 
                             QMainWindow, 
                             QPushButton, 
                             QTextEdit, 
                             QHBoxLayout,
                             QVBoxLayout,
                             QStackedWidget
                             ) 

from PyQt5.QtCore import Qt
        

def main():
    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()

    page1 = firstPage(QStackedWidget)

    stacked_widget.addWidget(page1)
    
    stacked_widget.setCurrentIndex(0)
    stacked_widget.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()