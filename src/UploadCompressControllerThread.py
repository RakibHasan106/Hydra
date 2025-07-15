from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
import time,os,shutil, queue
from pathlib import Path
from src import file_handler_fnc,compression
from src.uploaderThread import UploaderThread
from src.compresserThread import compresserThread

class UploadCompressControllerThread(QObject):
    finished = pyqtSignal()
    changeCompressionStatus = pyqtSignal(str)
    changeUploadStatus = pyqtSignal(str)

    def __init__(self,folder_path,conversionNeeded,compression_size_limit,chat_to_send,uploadNotNeeded):
        
        super().__init__()
        self.folder_path = folder_path
        # self.upload_queue = uploadTasks
        self.tasksQueue = queue.Queue()
        self.upload_queue = queue.Queue()
        
        self.is_compressionThread_running = False
        self.is_uploadThread_running = False
        
        self.conversionNeeded = conversionNeeded
        self.compression_size_limit = compression_size_limit

        self.chat_to_send = chat_to_send
        self.uploadNotNeeded = uploadNotNeeded
    
    def run(self):

        directory = Path(self.folder_path)
        for path in directory.iterdir():
            file_name = path.stem
            file_path = path

            if file_path.is_file():
                size = (os.path.getsize(file_path)/1000)/1000
                if file_handler_fnc.is_video(file_path):
                    
                    if size>2000 or file_path.suffix.lower()!='.mp4' or compression.get_resolution_label(file_path)=="high res":
                        
                        print("moving "+file_name+": "+str(size))
                        convert_path = os.path.join(file_path.parent,"convert")
                        
                        if not os.path.isdir(convert_path):
                            os.mkdir(convert_path)    

                        shutil.move(file_path,convert_path)
                        
                        print("moved!")

                        toBeConvertedFilePath = os.path.join(convert_path,file_path.name)

                        self.tasksQueue.put(toBeConvertedFilePath)
                        
                        #now start the compression
                        if(self.is_compressionThread_running==False and self.conversionNeeded==True) and self.compression_size_limit!="":
                            self.is_compressionThread_running = True
                            self.start_compression(self.compression_size_limit)
                            
                        

                    elif file_path.suffix=='.mp4' and not self.uploadNotNeeded:
                        
                        self.upload_queue.put(file_path)

                        if not self.is_uploadThread_running:
                            self.is_uploadThread_running=True
                            self.start_upload()
                            

                        print("waiting in the upload Queue: "+file_name)

                
                else:
                    # Here I will handle files those are not videos 
                    print("I am not a video , handle me wisely")
            


        # while(1):
        #     # time.sleep(1)
        #     if (not self.upload_queue.empty()) and not self.is_uploadThread_running:
        #         self.is_uploadThread_running = True
        #         self.start_upload()
            
        #     if not self.is_compressionThread_running and self.upload_queue.empty() and not self.is_uploadThread_running:
        #         break


        # self.finished.emit()

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(500)
        self._poll_timer.timeout.connect(self._poll_queues)
        self._poll_timer.start()

    def _poll_queues(self):
        if not self.upload_queue.empty() and not self.is_uploadThread_running and not self.uploadNotNeeded:
            self.is_uploadThread_running = True
            self.start_upload()

        # This is your "exit condition":
        if (not self.is_compressionThread_running
            and self.upload_queue.empty()
            and not self.is_uploadThread_running):
            self._poll_timer.stop()       # Stop the periodic checking
            self.finished.emit()          # Tell the system "I'm done!"

    
    def start_compression(self,compression_size_limit):
        
        target_size = float(compression_size_limit)
        
        #self.changeCompressionStatus.emit("compressing..."+os.path.basename(file_path)) # have to fix this
        
        self.compressThread = QThread()
        self.compressWorker = compresserThread(self.tasksQueue,target_size,self.upload_queue,self.uploadNotNeeded)

        self.compressWorker.moveToThread(self.compressThread)

        self.compressThread.started.connect(self.compressWorker.run)

        # self.compressWorker.progress.connect(self.update_compression_progress)
        # self.compressWorker.currentFileName.connect(self.update_compression_status)
        
        self.compressWorker.fileNamebeingCompressed.connect(self.update_compression_status)

        self.compressWorker.finished.connect(self.compression_completed)
        
        self.compressWorker.finished.connect(self.compressThread.quit)
        
        self.compressThread.finished.connect(self.compressThread.deleteLater)
        self.compressThread.finished.connect(self.compressWorker.deleteLater)

        self.compressThread.start()

    def start_upload(self):
        self.uploadWorker = UploaderThread(self.upload_queue,self.chat_to_send)
        self.uploaderThread = QThread()

        self.uploadWorker.moveToThread(self.uploaderThread)

        self.uploaderThread.started.connect(self.uploadWorker.run)

        self.uploadWorker.fileNamebeingUploaded.connect(self.update_upload_status)
        # self.uploadWorker.update.connect(self.progress_callback)
        # self.uploadWorker.current_uploadFile_name.connect(self.update_upload_status)

        self.uploadWorker.finished.connect(self.upload_completed)
        self.uploadWorker.finished.connect(self.uploaderThread.quit)
        
        self.uploaderThread.finished.connect(self.uploaderThread.deleteLater)
        self.uploaderThread.finished.connect(self.uploadWorker.deleteLater)

        self.uploaderThread.start()

    def update_compression_status(self,status):
        self.changeCompressionStatus.emit("Compressing : "+status+"....")
    
    def compression_completed(self):
        self.is_compressionThread_running = False
        self.changeCompressionStatus.emit("All Conversion Completed!!")

    def update_upload_status(self,status):
        self.changeUploadStatus.emit("Uploading : "+status+"....")

    def upload_completed(self):
        self.is_uploadThread_running = False
        self.changeUploadStatus.emit("All uploads in the current Queue finished!")