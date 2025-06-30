from PyQt5.QtWidgets import (QApplication,
                             QWidget,
                             QMainWindow,
                             QFileDialog,
                             QPushButton,
                             QVBoxLayout,
                             QLabel,
                             QProgressBar,
                             QComboBox,
                             QLineEdit,
                             QCheckBox
                             )

from PyQt5.QtCore import QThread, pyqtSignal, QObject
from qasync import asyncSlot

from pathlib import Path

import os, shutil, queue, time
from src import telegram_login,file_handler_fnc,compression
from src.uploaderThread import UploaderThread
from src.compresserThread import compresserThread
from src.UploadCompressControllerThread import UploadCompressControllerThread

class secondPage(QMainWindow):
    def __init__(self,stackedWidget):
        super().__init__()

        print("I am from second Page")

        self.abortUploading = False

        # path list of the files to be uploaded
        

        self.folder_path = None
        current_session = telegram_login.current_session_loader()
        self.client = telegram_login.get_client(current_session) if current_session!=None else None

        self.stackedWidget = stackedWidget
        self.setWindowTitle("Hydra")
        self.setFixedSize(500, 600)

        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)

        self.status_label = QLabel("Status: Idle")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        # select which chat to send
        self.dropdown = QComboBox()
        # self.dropdown.addItems(["Option 1", "Option 2","Option 3"])
        self.dropdown.currentIndexChanged.connect(self.on_selection_change)
        self.chat_to_send = self.dropdown.currentData()
        
        self.chat_list = []
        if self.client != None :
            for dialog in self.client.iter_dialogs():
                self.chat_list.append(dialog.entity)
                self.dropdown.addItem(dialog.name,dialog.entity)

        if self.client != None :
            self.client.disconnect()

        #Button to start the uploading
        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.upload_button_clicked)

        #Abort Button
        self.abort_button = QPushButton("Abort Upload")
        # self.abort_button.clicked.connect(self.abort_upload)

        #checkerBox if user want to compress now or just move to a separate folder for converting later
        self.convertCheckbox = QCheckBox("Convert Unsupported Videos now?")
        self.convertCheckbox.stateChanged.connect(self.checkbox_changed)
        self.conversionNeeded = False

        #Thread update show
        self.compression_status = QLabel("No compression going on...")
        self.compression_progress = QProgressBar()
        self.compression_progress.setValue(0)

        self.compression_size_limit = QLineEdit()
        self.compression_size_limit.setPlaceholderText("In MB")
        self.compression_size_limit.setDisabled(True)

        
        
        


        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        vbox = QVBoxLayout()
        vbox.addWidget(self.select_folder_btn)
        vbox.addWidget(self.dropdown)

        vbox.addWidget(self.convertCheckbox)

        vbox.addWidget(self.compression_size_limit)
        
        vbox.addWidget(self.upload_button)
        
        vbox.addWidget(self.status_label)
        vbox.addWidget(self.progress_bar)

        vbox.addWidget(self.abort_button)

       

        vbox.addWidget(self.compression_status)
        vbox.addWidget(self.compression_progress)



        central_widget.setLayout(vbox)
        # self.setMinimumSize(500,600)

        # print("successfully logged in!!!!! you done quite a good job! proud of you")
    
    def on_selection_change(self,idx):
        self.chat_to_send = self.dropdown.itemData(idx)
 
    
    def abort_upload(self):
        self.status_label.setText("Aborting upload....")
        self.abortUploading = True

    def select_folder(self):
        self.folder_path = QFileDialog.getExistingDirectory(None,"Select Folder")
        

    def upload_button_clicked(self):

        if self.chat_to_send==None or self.folder_path == None:
            return

        self.dropdown.setEnabled(False)
        self.select_folder_btn.setEnabled(False)
        self.upload_button.setEnabled(False)
        self.convertCheckbox.setEnabled(False)
        self.compression_size_limit.setEnabled(False)

        self.controllWorker = UploadCompressControllerThread(self.folder_path,self.conversionNeeded,self.compression_size_limit.text(),self.chat_to_send)
        self.controllThread = QThread()

        self.controllWorker.moveToThread(self.controllThread)

        self.controllThread.started.connect(self.controllWorker.run)
        
        self.controllWorker.changeCompressionStatus.connect(self.update_compression_status)
        self.controllWorker.changeUploadStatus.connect(self.update_upload_status)


        self.controllWorker.finished.connect(self.all_tasks_completed)
        self.controllWorker.finished.connect(self.controllThread.quit)
        
        self.controllThread.finished.connect(self.controllThread.deleteLater)
        self.controllThread.finished.connect(self.controllWorker.deleteLater)

        self.controllThread.start()

    def update_compression_status(self,status):
        self.compression_status.setText(status) 
        
    def update_upload_status(self,status):
        self.status_label.setText(status)
        

    def all_tasks_completed(self):
        self.dropdown.setEnabled(True)
        self.select_folder_btn.setEnabled(True)
        self.upload_button.setEnabled(True)
        self.convertCheckbox.setEnabled(True)
        self.compression_size_limit.setEnabled(True)

    def progress_callback(self,percent):
            
            print(percent)
            # Only update if percent changed
            self.progress_bar.setValue(percent)


    def update_compression_progress(self,progress):
        self.compression_progress.setValue(progress)
    
    
    # def upload_finished(self):
    #     self.status_label.setText("Upload Finished!")
    #     self.is_uploadThread_running = False

    def checkbox_changed(self,state):
        if self.convertCheckbox.isChecked():
            self.conversionNeeded = True
            self.compression_size_limit.setEnabled(True)
        
        else:
            self.conversionNeeded = False   
            self.compression_size_limit.setEnabled(False)
    