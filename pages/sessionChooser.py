from PyQt5.QtWidgets import(
    QApplication,
    QWidget,
    QMainWindow,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QComboBox,
)
import asyncio
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from src import telegram_login
from pages import secondPage
class saved_session_login_worker(QObject):
    finished = pyqtSignal()
    login_status = pyqtSignal(bool)
    def __init__(self,session_details):
        super().__init__()
        self.session_details = session_details
    
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.login())
        loop.close()
        self.finished.emit()
    
    async def login(self):
        a = await telegram_login.saved_info_login(self.session_details)
        self.login_status.emit(a)
    
class sessionChooserPage(QMainWindow):
    def __init__(self,stackedWidget):
        super().__init__()
        self.stackedWidget = stackedWidget

        self.setWindowTitle("Hydra")
        self.setFixedSize(500,600)
        

        #session's list
        self.dropDownSession = QComboBox()
        sessions = telegram_login.session_loader()
        
        if sessions != None :
            for session in sessions:
                self.dropDownSession.addItem(session["user_name"],session)
        
        self.dropDownSession.currentIndexChanged.connect(self.on_selection_change)
        self.currentSession = self.dropDownSession.currentData()

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login_button_clicked)
        
        self.add_another_acc_btn = QPushButton("Add Another Account")
        self.add_another_acc_btn.clicked.connect(self.add_another_acc_btn_clicked)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        vbox = QVBoxLayout()
        vbox.addWidget(self.dropDownSession)
        vbox.addWidget(self.login_button)
        vbox.addWidget(self.add_another_acc_btn)
        

        central_widget.setLayout(vbox)
    
    def on_selection_change(self,idx):
        self.currentSession = self.dropDownSession.itemData(idx)

    def add_another_acc_btn_clicked(self):
        self.stackedWidget.setCurrentIndex(1)

    def login_button_clicked(self):
        
        #now create a thread and use that thread to login.
        self.thread = QThread()
        self.worker = saved_session_login_worker(self.currentSession)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.login_status.connect(self.is_login_successfull)
        
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.worker.deleteLater)
        

        self.thread.start()

    def is_login_successfull(self,chk):
        if chk == True :
            self.stackedWidget.setCurrentIndex(2)
        
        
    
    