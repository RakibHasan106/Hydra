from PyQt5.QtWidgets import (QApplication, 
                             QWidget, 
                             QMainWindow,
                             QLineEdit,
                             QPushButton,
                             QVBoxLayout,
                             QHBoxLayout,
                             QMessageBox
                             )

from src import telegram_login,loginThread
import json,os
from pages.secondPage import secondPage
from PyQt5.QtCore import QObject, pyqtSignal, QThread

class firstPage(QMainWindow):
    def __init__(self,stackedWidget):
        super().__init__()
        self.stackedWidget = stackedWidget
        
        self.login_error = None



        self.setWindowTitle("Telegram Sender")
        # self.setGeometry(1300,200,500,600)
        self.setFixedSize(500, 600)
        # self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        # Text Areas for api id and api hash
        self.api_id_text_area = QLineEdit()
        self.api_hash_text_area = QLineEdit()
        self.phone_number = QLineEdit()
        self.sent_code = QLineEdit()
        

        self.sent_code.setDisabled(True)

        self.api_id_text_area.setPlaceholderText("API ID")
        self.api_hash_text_area.setPlaceholderText("API Hash Code")

        # Buttons
        self.sent_code_btn = QPushButton("Send Code")
        self.sent_code_btn.clicked.connect(self.send_code_button_clicked)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login_button_clicked)
        self.login_button.setDisabled(True)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.api_id_text_area)
        vbox.addWidget(self.api_hash_text_area)
        vbox.addWidget(self.phone_number)
        vbox.addWidget(self.sent_code_btn)

        vbox.addWidget(self.sent_code)
        vbox.addWidget(self.login_button)
        

        central_widget.setLayout(vbox)
        # self.setMinimumSize(500, 600)
    def send_code_button_clicked(self):

        api_id = self.api_id_text_area.text()
        api_hash = self.api_hash_text_area.text()
        phone_number = self.phone_number.text()

        if(api_id == "" or api_hash== "" or phone_number== ""):
            QMessageBox.warning(self,"warning","some required fields are empty")
            return
        
        self.worker = loginThread.login_worker(api_id,api_hash,phone_number)
        self.thread = QThread()

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        
        self.worker.error.connect(self.set_error)
        self.worker.finished.connect(self.check_error)

        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.worker.deleteLater)
        
        self.thread.start()
        

        # self.client = telegram_login.send_code(api_id,api_hash,phone_number)
        
        # if (self.client==None):
        #     QMessageBox.warning(self,"warning","your credentials werer wrong or any other error happened which I don't know about!")
        #     return
        
        self.api_id_text_area.setDisabled(True)
        self.api_hash_text_area.setDisabled(True)
        self.sent_code_btn.setDisabled(True)
        self.phone_number.setDisabled(True)
        
        self.sent_code.setDisabled(False)
        self.login_button.setDisabled(False)

        # now I have to return a client perfectly from the send_code function


        # if telegram_login.send_code(api_id,api_hash):
        #     self.stackedWidget.setCurrentIndex()

    def login_button_clicked(self):
        entered_code = self.sent_code.text()
        if entered_code=="":
            QMessageBox.warning(self,"warning","Entered Code is empty")
            return
        

        self.worker.enter_code(entered_code)
              
        
        # page2 = secondPage(self.stackedWidget)
        # self.stackedWidget.addWidget(page2)
        # self.stackedWidget.setCurrentIndex(1)

    def check_error(self):
        if self.login_error != None:
            print("error not here")
            self.stackedWidget.setCurrentIndex(2)
            print("error seems to be here!")

    def set_error(self,e):
        self.login_error = e
        
