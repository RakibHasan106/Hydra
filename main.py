
import sys,os
from pages.firstPage import firstPage
from pages.secondPage import secondPage
from pages.thirdPage import thirdPage
import json
from src import telegram_login
import asyncio,threading

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

    page1 = firstPage(stacked_widget)
    page2 = secondPage(stacked_widget)
    # page3 = thirdPage(stacked_widget)

    stacked_widget.addWidget(page1)
    stacked_widget.addWidget(page2)
    # stacked_widget.addWidget(page3)

    session_details = telegram_login.session_loader()
    
    logged_in = telegram_login.saved_info_login(session_details) if session_details!=None else False
        
    if(logged_in!=False):
        print("here I am")
        stacked_widget.setCurrentIndex(1)

    else:
        stacked_widget.setCurrentIndex(0)

    stacked_widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()