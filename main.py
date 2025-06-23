
import sys,asyncio
from pages.firstPage import firstPage
from pages.secondPage import secondPage
from pages.sessionChooser import sessionChooserPage
from src import telegram_login
from qasync import QEventLoop, asyncSlot, QApplication

from PyQt5.QtWidgets import (QWidget,  
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

    page1 = sessionChooserPage(stacked_widget)
    page2 = firstPage(stacked_widget)
    page3 = secondPage(stacked_widget)

    stacked_widget.addWidget(page1)
    stacked_widget.addWidget(page2)
    stacked_widget.addWidget(page3)

    sessions = telegram_login.session_loader()

    print(sessions)

    if sessions == None:
        stacked_widget.setCurrentIndex(1)
    else:
        stacked_widget.setCurrentIndex(0)
    
    # logged_in = telegram_login.saved_info_login(session_details) if session_details!=None else False
        
    # if(logged_in!=False):
    #     page2 = secondPage(stacked_widget)
    #     stacked_widget.addWidget(page2)
    #     stacked_widget.setCurrentIndex(1)

    # else:
    #     print("first page")
    #     stacked_widget.setCurrentIndex(0)

    stacked_widget.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()