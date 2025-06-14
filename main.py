
import sys,asyncio
from pages.firstPage import firstPage
from pages.secondPage import secondPage
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

    page1 = firstPage(stacked_widget)
    # page3 = thirdPage(stacked_widget)

    stacked_widget.addWidget(page1)
    
    # stacked_widget.addWidget(page3)

    session_details = telegram_login.session_loader()
    
    logged_in = telegram_login.saved_info_login(session_details) if session_details!=None else False
        
    if(logged_in!=False):
        page2 = secondPage(stacked_widget)
        stacked_widget.addWidget(page2)
        stacked_widget.setCurrentIndex(1)

    else:
        print("first page")
        stacked_widget.setCurrentIndex(0)

    stacked_widget.show()

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()