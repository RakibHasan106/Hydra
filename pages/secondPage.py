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

# class compression_Worker(QObject):
#     finished = pyqtSignal()
#     progress = pyqtSignal(int)
#     currentFileName = pyqtSignal(str)
    
#     def __init__(self,tasksQueue,targetSize):
#         super().__init__()
#         self.tasksQueue = tasksQueue
#         self.targetSize = targetSize

#     def run(self):
#         task = 1
        
#         while not self.tasksQueue.empty():
            
#             #here do the compression task.
#             file_path = self.tasksQueue.get(timeout=1)
#             self.currentFileName.emit(file_path)
            
#             # time.sleep(2)
#             # try:
#             #     compression.compress(file_path,self.targetSize)
#             #     # os.remove(file_path)
#             # except Exception as E:
#             #     print(E)
            
#             self.tasksQueue.task_done()    
            
#             self.progress.emit(task)

#             print("compressed : "+str(self.currentFileName))
            
#             task = task+1
        
#         self.finished.emit()



class secondPage(QMainWindow):
    def __init__(self,stackedWidget):
        super().__init__()

        print("I am from second Page")

        self.abortUploading = False

        # path list of the files to be uploaded
        self.upload_queue = queue.Queue()

        self.folder_path = None
        current_session = telegram_login.current_session_loader()
        self.client = telegram_login.get_client(current_session) if current_session!=None else None

        self._last_percent = 0

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

        # Thread Running status
        self.is_compressionThread_running = False
        # if uploader Thread is running
        self.is_uploadThread_running = False

        # Compression Task Queue
        
        self.tasksQueue = queue.Queue()


        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        vbox = QVBoxLayout()
        vbox.addWidget(self.select_folder_btn)
        vbox.addWidget(self.dropdown)

        vbox.addWidget(self.convertCheckbox)

        vbox.addWidget(self.compression_size_limit)
        
        vbox.addWidget(self.upload_button)
        vbox.addWidget(self.progress_bar)


        vbox.addWidget(self.abort_button)

        vbox.addWidget(self.status_label)

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
        

    def upload_button_clicked(self):

        # await self.client.disconnect()
        # current_session = telegram_login.session_loader()
        # self.client = telegram_login.get_client(current_session)
        # await self.client.connect() 

        if self.chat_to_send==None or self.folder_path == None or self.compression_size_limit.text()=="":
            return

        self.dropdown.setEnabled(False)
        self.select_folder_btn.setEnabled(False)
        self.upload_button.setEnabled(False)
        self.convertCheckbox.setEnabled(False)
        self.compression_size_limit.setEnabled(False)

        directory = Path(self.folder_path)
        for path in directory.iterdir():
            file_name = path.stem
            file_path = path

            if file_path.is_file():
                size = (os.path.getsize(file_path)/1000)/1000
                if file_handler_fnc.is_video(file_path):
                    
                    if size>2000 or file_path.suffix.lower()!='.mp4' or compression.get_resolution_label(file_path)=="high res":
                        print("moving "+file_name)
                        convert_path = os.path.join(file_path.parent,"convert")
                        if not os.path.isdir(convert_path):
                            os.mkdir(convert_path)    

                        shutil.move(file_path,convert_path)
                        
                        print("moved!")

                        toBeConvertedFilePath = os.path.join(convert_path,file_path.name)

                        self.tasksQueue.put(toBeConvertedFilePath)
                        
                        #now start the compression
                        if(self.is_compressionThread_running==False and self.conversionNeeded==True):
                            self.start_compression(toBeConvertedFilePath,self.compression_size_limit.text())
                            self.is_compressionThread_running = True
                        


                    elif file_path.suffix=='.mp4':

                        print("uploading "+file_name)
                        
                        self.status_label.setText(f"Uploading {file_path.name}....")

                        self.upload_queue.put(file_path)

                        if not self.is_uploadThread_running:
                            self.startUpload()
                            self.is_uploadThread_running=True

                        # duration, width, height = file_handler_fnc.get_video_metadata(file_path)
                        # thumb = file_handler_fnc.extract_thumbnail(file_path)

                        # try:
                        #     media = await fast_upload(
                        #                         self.client, 
                        #                         file_location=file_path, 
                        #                         name=file_name+".mp4", 
                        #                         progress_bar_function=self.progress_callback
                        #                         )
                        
                        #     await self.client.send_file(
                        #         entity=self.chat_to_send.id,
                        #         file=media,
                        #         caption=file_name,
                        #         thumb=thumb,
                        #         supports_streaming=True,
                        #         attributes=[
                        #             DocumentAttributeVideo(
                        #                 duration = duration,
                        #                 w = width,
                        #                 h = height,
                        #                 supports_streaming = True
                        #             )
                        #         ]
                        #     )
                        #     os.remove(file_path)

                        # except Exception as e: 
                        #     print(e)

                        
                        #now delete the file

                        
                        # os.remove(thumb)
                        
                        # if self.abort_upload == True:
                        #     self.abort_upload = False
                        #     self.status_label.setText("Upload Aborted By User")
                        #     break
                
                else:
                    # Here I will handle files those are not videos 
                    print("I am not a video , handle me wisely")
            

        # if(self.abort_upload!=True):
        #     self.status_label.setText("All uploads complete")
        
        self.dropdown.setEnabled(True)
        self.select_folder_btn.setEnabled(True)
        self.upload_button.setEnabled(True)


    def progress_callback(self,percent):
            
            print(percent)
            # Only update if percent changed
            self.progress_bar.setValue(percent)
    
    def select_folder(self):
        self.folder_path = QFileDialog.getExistingDirectory(None,"Select Folder")
        # files = os.listdir(self.folder_path)

    def start_compression(self,file_path,compression_size_limit):
        
        target_size = float(compression_size_limit)
        self.compression_status.setText("compressing...")
        self.compressThread = QThread()
        self.compressWorker = compresserThread(self.tasksQueue,target_size)

        self.compressWorker.moveToThread(self.compressThread)

        self.compressThread.started.connect(self.compressWorker.run)

        # self.compressWorker.progress.connect(self.update_compression_progress)
        # self.compressWorker.currentFileName.connect(self.update_compression_status)
        
        self.compressWorker.finished.connect(self.compression_completed)
        self.compressWorker.finished.connect(self.compressThread.quit)
        self.compressWorker.finished.connect(self.compressThread.deleteLater)
        self.compressThread.finished.connect(self.compressWorker.deleteLater)

        self.compressThread.start()

    def update_compression_status(self,status):
        self.compression_status.setText("compressing "+os.path.basename(status))

    def update_compression_progress(self,progress):
        self.compression_progress.setValue(progress)
    
    def compression_completed(self):
        self.is_compressionThread_running = False
        self.compression_status.setText("completed!")
    

    def startUpload(self):
        self.uploadWorker = UploaderThread(self.upload_queue,self.chat_to_send)
        self.uploaderThread = QThread()

        self.uploadWorker.moveToThread(self.uploaderThread)

        self.uploaderThread.started.connect(self.uploadWorker.run)

        self.uploadWorker.update.connect(self.progress_callback)

        self.uploadWorker.finished.connect(self.upload_finished)
        self.uploadWorker.finished.connect(self.uploaderThread.quit)
        self.uploadWorker.finished.connect(self.uploaderThread.deleteLater)
        self.uploaderThread.finished.connect(self.uploadWorker.deleteLater)

        self.uploaderThread.start()

    def upload_finished(self):
        self.status_label.setText("Upload Finished!")
        self.is_uploadThread_running = False

    def checkbox_changed(self,state):
        if self.convertCheckbox.isChecked():
            self.conversionNeeded = True
            self.compression_size_limit.setEnabled(True)
        
        else:
            self.conversionNeeded = False   
            self.compression_size_limit.setEnabled(False)
    