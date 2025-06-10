from PyQt5.QtWidgets import (QApplication, 
                             QWidget, 
                             QMainWindow,
                             QLineEdit,
                             QPushButton,
                             QVBoxLayout,
                             QHBoxLayout,
                             QMessageBox
                             )

from src import telegram_login
import json,os


class firstPage(QMainWindow):
    def __init__(self,stackedWidget):
        super().__init__()
        self.stackedWidget = stackedWidget
        
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
        

        self.client = telegram_login.send_code(api_id,api_hash,phone_number)
        
        if (self.client==None):
            QMessageBox.warning(self,"warning","your credentials werer wrong or any other error happened which I don't know about!")
            return
        
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

        temp_client = telegram_login.login(self.client, entered_code)

        if( temp_client  == None ):
            QMessageBox.warning(self,"warning","Your Entered Code is wrong!")
            return
        else:
            self.client = temp_client


        session_path = os.path.join("./session","saved_session.session")

        data = {
            "session_name" : session_path,
            "api_id" : self.api_id_text_area.text(),
            "api_hash" : self.api_hash_text_area.text()
        }
        
        json_path = os.path.join("./session","LastSavedSession.json")
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)
        
        self.stackedWidget.setCurrentIndex(1)

        
