from PyQt5.QtWidgets import (QApplication, 
                             QWidget, 
                             QMainWindow,
                             QTextEdit,
                             QPushButton,
                             QVBoxLayout,
                             QHBoxLayout
                             )



class firstPage(QMainWindow):
    def __init__(self,stackedWidget):
        super().__init__()
        self.stackedWidget = stackedWidget
        
        self.setWindowTitle("Telegram Sender")
        self.setGeometry(1300,200,400,400)
        # self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        # Text Areas for api id and api hash
        self.api_id_text_area = QTextEdit()
        self.api_hash_text_area = QTextEdit()

        self.api_id_text_area.setPlaceholderText("API ID")
        self.api_hash_text_area.setPlaceholderText("API Hash Code")

        # Buttons
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login_to_telegram)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.api_id_text_area)
        vbox.addWidget(self.api_hash_text_area)
        vbox.addWidget(self.login_button)

        central_widget.setLayout(vbox)

    def login_to_telegram(self):
        api_id = self.api_id_text_area.toPlainText()
        api_hash_code = self.api_hash_text_area.toPlainText()

        
        # print(api_id)
        # print(api_hash_code)


