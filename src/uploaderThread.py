from PyQt5.QtCore import QObject, QThread, pyqtSignal
import asyncio,os
from src import file_handler_fnc,telegram_login
from FastTelethonhelper import fast_upload
from telethon.sync import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
from pathlib import Path

class UploaderThread(QObject):
    finished = pyqtSignal()
    update = pyqtSignal(float)

    def __init__(self,uploadQueue,chat_to_send):
        super().__init__()
        self.uploadQueue = uploadQueue
        self.chat_to_send = chat_to_send

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.upload())
        loop.close()
        self.finished.emit()

    async def upload(self):
        #connecting the client for uploading
        current_session = telegram_login.current_session_loader()
        client = TelegramClient(
            current_session["session_name"],
            current_session["api_id"],
            current_session["api_hash"]
        )
        await client.connect()
        print("client connected successfully for upload")

        while not self.uploadQueue.empty():
            file_path = self.uploadQueue.get()

            file_name = file_path.stem

            print(f"uploading {file_name}...")

            duration, width, height = file_handler_fnc.get_video_metadata(file_path)
            thumb = file_handler_fnc.extract_thumbnail(file_path)

            try:
                media = await fast_upload(
                                            client, 
                                            file_location=file_path, 
                                            name=file_name+".mp4", 
                                            progress_bar_function=self.progress_callback
                                        )
                        
                await client.send_file(
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
                
                os.remove(file_path)

            except Exception as e: 
                print(e)

                        
            os.remove(thumb)
                        
                        # if self.abort_upload == True:
                        #     self.abort_upload = False
                        #     self.status_label.setText("Upload Aborted By User")
                        #     break
    
    def progress_callback(self,done,total):
        percent = (total/done)*100
        print("progress callback is being called")
        
        self.update.emit(percent)