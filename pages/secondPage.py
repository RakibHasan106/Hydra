from PyQt5.QtWidgets import (QApplication,
                             QWidget,
                             QMainWindow,
                             QFileDialog,
                             QPushButton,
                             QVBoxLayout
                             )

import os, shutil

class secondPage(QMainWindow):
    def __init__(self,stackedWidget):
        super().__init__()

        self.stackedWidget = stackedWidget
        self.setWindowTitle("Telegram Sender")
        self.setFixedSize(500, 600)

        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        vbox = QVBoxLayout()
        vbox.addWidget(self.select_folder_btn)

        central_widget.setLayout(vbox)
        # self.setMinimumSize(500,600)


        # print("successfully logged in!!!!! you done quite a good job! proud of you")

    def select_folder(self):
        self.folder_path = QFileDialog.getExistingDirectory(None,"Select Folder")
        # files = os.listdir(self.folder_path)

        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                file_path = os.path.join(root,file)
                size = (os.path.getsize(file_path)/1000)/1000

                if (size>2000):
                    convert_path = os.path.join(root,"convert")
                    if not os.path.isdir(convert_path):
                        os.mkdir(convert_path)    
                    
                    shutil.move(file_path,convert_path)

                else:
                    pass