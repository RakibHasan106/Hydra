from PyQt5.QtWidgets import (QApplication,
                             QWidget,
                             QMainWindow,
                             QFileDialog,
                             QPushButton,
                             QVBoxLayout,
                             QLabel,
                             QProgressBar,
                             QComboBox
                             )
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from qasync import asyncSlot
from collections import deque
from FastTelethonhelper import fast_upload
from moviepy import VideoFileClip
from telethon.tl.types import DocumentAttributeVideo

import asyncio,subprocess

import os, shutil
from src import telegram_login

def extract_thumbnail(video_path, thumb_path='thumb.jpg'):
    cmd = [
        'ffmpeg', '-ss' , '00:00:02', '-i', video_path,
        '-frames:v', '1', '-q:v', '2', thumb_path, '-y'
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return thumb_path

class secondPage(QMainWindow):
    def __init__(self,stackedWidget):
        super().__init__()

        self.abortUploading = False

        self.folder_path = None
        current_session = telegram_login.session_loader()
        self.client = telegram_login.get_client(current_session) if current_session!=None else None

        self._last_percent = 0

        self.stackedWidget = stackedWidget
        self.setWindowTitle("Telegram Sender")
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

        #Button to start the uploading
        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.upload_button_clicked)

        #Abort Button
        self.abort_button = QPushButton("Abort Upload")
        self.abort_button.clicked.connect(self.abort_upload)

        #client disconnect button

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect_button_clicked)


        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        vbox = QVBoxLayout()
        vbox.addWidget(self.select_folder_btn)
        vbox.addWidget(self.dropdown)

        vbox.addWidget(self.upload_button)
        vbox.addWidget(self.progress_bar)

        vbox.addWidget(self.abort_button)

        vbox.addWidget(self.disconnect_button)

        vbox.addWidget(self.status_label)



        central_widget.setLayout(vbox)
        # self.setMinimumSize(500,600)


        # print("successfully logged in!!!!! you done quite a good job! proud of you")
    def on_selection_change(self,idx):
        self.chat_to_send = self.dropdown.itemData(idx)

    def get_video_metadata(self,path):
        clip = VideoFileClip(path)
        duration = int(clip.duration)
        width = clip.w 
        height = clip.h
        clip.close()
        return duration, width , height
    
    def abort_upload(self):
        self.status_label.setText("Aborting upload....")
        self.abortUploading = True
        

    
    @asyncSlot()
    async def upload_button_clicked(self):

        await self.client.disconnect()
        current_session = telegram_login.session_loader()
        self.client = telegram_login.get_client(current_session)
        await self.client.connect()

        if self.chat_to_send==None or self.folder_path == None:
            return

        self.dropdown.setEnabled(False)
        self.select_folder_btn.setEnabled(False)
        self.upload_button.setEnabled(False)

        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                file_name = file
                file_path = os.path.join(root,file)
                size = (os.path.getsize(file_path)/1000)/1000
                
                if (size>2000) or not self.is_media(file_path):
                    convert_path = os.path.join(root,"convert")
                    if not os.path.isdir(convert_path):
                        os.mkdir(convert_path)    
                    
                    #now have to go into the compression world

                    shutil.move(file_path,convert_path)

                    
                else:
                    # print("I am doing my job: uploading")
                    print(file_name)
                    # await self.upload_file(file_path,file_name)
                    self.status_label.setText(f"Uploading {os.path.basename(file_path)}....")
                    
                    duration, width, height = self.get_video_metadata(file_path)
                    thumb = extract_thumbnail(file_path)

                    try:
                        media = await fast_upload(
                                              self.client, 
                                              file_location=file_path, 
                                              name=file_name, 
                                              progress_bar_function=self.progress_callback
                                            )
                    
                        await self.client.send_file(
                            entity=self.chat_to_send.id,
                            file=media,
                            caption=file_name,
                            thumb=thumb,
                            supports_streaming=True,
                            attributes=[
                                DocumentAttributeVideo(
                                    duration = duration,
                                    w = width,
                                    h = height,
                                    supports_streaming = True
                                )
                            ]
                        )

                    except Exception as e: 
                        print(e)

                    
                    #now delete the file
                    #  as there is problem with this code , 
                    # still not implementing the video delete logic

                    # upload_path = os.path.join(root,"upload")
                    # if not os.path.isdir(upload_path):
                    #     os.mkdir(upload_path)    

                    # shutil.move(file_path,upload_path)

                    os.remove(file_path)
                    os.remove(thumb)
                    

                    if self.abort_upload == True:
                        self.abort_upload = False
                        self.status_label.setText("Upload Aborted By User")
                        break
                    
        if(self.abort_upload!=True):
            self.status_label.setText("All uploads complete")
        
        self.dropdown.setEnabled(True)
        self.select_folder_btn.setEnabled(True)
        self.upload_button.setEnabled(True)


    def progress_callback(self,sent_bytes, total_bytes):
            percent = int((sent_bytes / total_bytes) * 100)
            print(percent)
            # Only update if percent changed
            
            if percent != getattr(self, '_last_percent', None):
                self.progress_bar.setValue(percent)
                self._last_percent = percent

            return "progressed!"
    
    def select_folder(self):
        self.folder_path = QFileDialog.getExistingDirectory(None,"Select Folder")
        # files = os.listdir(self.folder_path)
    
    # async def upload_file(self,file_path,file_name):
    #     self._last_percent = 0
    #     try:
    #         file_size = os.path.getsize(file_path)
    #         self.status_label.setText(f"Uploading {os.path.basename(file_path)}....")
    #         # await asyncio.sleep(100)

    #         # Custom progress callback function
        
    #         def progress_callback(sent_bytes, total_bytes):
    #             percent = int((sent_bytes / total_bytes) * 100)
    #             # Only update if percent changed
    #             if percent != getattr(self, '_last_percent', None):
    #                 self.progress_bar.setValue(percent)
    #                 self._last_percent = percent
            
    #         if self.client == None:
    #             print("client is none")


    #         print(self.chat_to_send.id)
    #         # Send file to "Saved Messages" with progress
    #         try:
    #             await self.client.send_file(
    #                 entity=self.chat_to_send.id,
    #                 file=file_path,
    #                 caption=file_name,
    #                 progress_callback=progress_callback,
    #                 part_size_kb=4096
    #             )
    #         except Exception as e:
    #             print(e)   
            

    #         self.status_label.setText(f"Uploaded {os.path.basename(file_path)}")

    #     except Exception as e:
    #         self.status_label.setText(f"Error: {str(e)}")
    
    

    # def start_next_upload(self):
    #     if not self.upload_queue:
    #         self.status_label.setText("All uploads complete.")
    #         return

    #     file_path = self.upload_queue.popleft()
    #     self.upload_worker = upload_worker(file_path, self.client,self.chat_to_send)
    #     self.upload_thread = QThread()  # Create a new thread

    #     self.upload_worker.moveToThread(self.upload_thread)
    #     self.upload_thread.started.connect(self.upload_worker.run)
    #     self.upload_worker.progress.connect(self.progress_bar.setValue)
    #     self.upload_worker.status.connect(self.status_label.setText)
    #     self.upload_worker.finished.connect(self.upload_thread.quit)
    #     self.upload_worker.finished.connect(self.start_next_upload)
    #     self.upload_worker.finished.connect(self.upload_worker.deleteLater)
    #     self.upload_thread.finished.connect(self.upload_thread.deleteLater)

    #     self.upload_thread.start()
                    

    def is_media(self,file_path):
        
        MEDIA_EXTENSIONS = {
            "image": ['.jpg', '.jpeg', '.png', '.webp'],
            "video": ['.mp4'],  # must be H.264 + AAC
            "gif": ['.gif'],
            "audio": ['.mp3', '.m4a', '.ogg', '.wav', '.flac']
        }
        
        ext = os.path.splitext(file_path)[1].lower()
    
        for media_type, extensions in MEDIA_EXTENSIONS.items():
            if ext in extensions:
                return True
        
        return False
    
    def disconnect_button_clicked(self):
        if self.client!=None : 
            self.client.disconnect()