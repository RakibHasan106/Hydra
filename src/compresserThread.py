from PyQt5.QtCore import QObject, pyqtSignal

import os
import subprocess,json
from pathlib import Path
from moviepy import VideoFileClip
from send2trash import send2trash
from src import file_handler_fnc

class compresserThread(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal()
    fileNamebeingCompressed = pyqtSignal(str)

    def __init__(self,fileQueue,targetSize,upload_queue,uploadNotNeeded):
        super().__init__()
        self.fileQueue = fileQueue
        self.targetSize = targetSize
        self.upload_queue = upload_queue
        self.uploadNotNeeded = uploadNotNeeded

    def run(self):
        encoder = detect_gpu_encoder()
        while not self.fileQueue.empty():
             file = self.fileQueue.get()
             file_path = Path(file)
             size = (os.path.getsize(file_path)/1000)/1000

             output_path = os.path.join(file_path.parent,"compressed",file_path.stem+"_compressed.mp4")
             os.makedirs(os.path.dirname(output_path), exist_ok=True)

             if not Path(file).is_dir():
                self.fileNamebeingCompressed.emit(file_path.name)
                if size>2000:
                    print("I am dual pass")
                    
                    print("compressing - "+Path(file).name+"...")
                    

                    if file_handler_fnc.is_old_video(file_path):
                        process_args = [
                            "ffmpeg", "-i", f"{str(file)}"
                        ]

                        if get_resolution_label(file)=="high res":
                            process_args.extend(["-vf","scale=1920:1080"])
                        
                        # cmd_args = " ".join(process_args)
                        
                        process_args.extend([
                             "-c:v", encoder,
                            "-c:a", "aac",
                            str(output_path)
                        ])

                        try:
                            subprocess.check_call(process_args)
                        except:
                            print("encountered an error during compressing : "+ file_path.name)


                        temp_size = (os.path.getsize(output_path)/1000)/1000
                        if(temp_size>2000):
                            os.remove(output_path)
                        else:
                            if self.uploadNotNeeded != True : 
                                self.upload_queue.put(Path(output_path))
                            os.remove(file)
                            # send2trash(file)
                            continue

                    expected_bitrate = calculate_video_bitrate(file,float(self.targetSize))
                    print(expected_bitrate)
                    cmd_args = ["ffmpeg", "-i" , str(file), "-y"]
                    
                    if get_resolution_label(file)=="high res":
                        cmd_args.extend(["-vf","scale=1920:1080"])

                    process_args_pass_1 =cmd_args + [
                        "-b:v", str(expected_bitrate)+"k",
                        "-c:v", encoder, 
                        "-pass", "1",
                        "-an", #meaning audio off
                        "-f",
                        "mp4",
                        f"{os.path.join(os.path.dirname(file),"TEMP")}" # this means output won't be saved
                    ]
                    
                    # cmd_args_1 = " ".join(process_args_pass_1)
                    
                    process_args_pass_2 = cmd_args + [
                        "-b:v", str(expected_bitrate)+"k",
                        "-c:v", encoder,
                        "-pass", "2",
                        "-c:a", "aac",
                        str(output_path)
                    ]
                    # cmd_args_2 = " ".join(process_args_pass_2)

                    try:
                        subprocess.check_call(process_args_pass_1)
                        subprocess.check_call(process_args_pass_2)
                        
                        if self.uploadNotNeeded != True : 
                                self.upload_queue.put(Path(output_path))
                        
                        os.remove(file)
                        # send2trash(file)
                    except:
                        print("encountered an error during compressing : "+ file_path.name)
                    
                else:
                    
                    process_args = [
                        "ffmpeg", "-i", f"{str(file)}",
                        "-c:v", encoder,
                        "-c:a", "aac",
                        str(output_path)
                    ]
                    # cmd_args = " ".join(process_args)

                    try:
                        subprocess.check_call(process_args)
                        
                        if self.uploadNotNeeded != True : 
                                self.upload_queue.put(Path(output_path))
                        
                        os.remove(file)
                        # send2trash(file)
                    except:
                        print("encountered an error during compressing : "+ file_path.name)
                    
                    # p1 = subprocess.Popen(f'start cmd /k "{cmd_args}"', shell=True)
                    # p1.wait()
                # os.remove(file)

        self.finished.emit()
             

def calculate_video_bitrate(file_path, target_size_mb):
    clip = VideoFileClip(file_path)
    v_len = clip.duration
    clip.close()
    print(f"Video duration: {v_len} seconds")
    a_rate = get_audio_bitrate(file_path)
    print(f"Audio Bitrate: {a_rate}k")
    total_bitrate = (target_size_mb * 8192.0 * 0.98) / (v_len) - a_rate
    return max(1, round(total_bitrate)) 

def get_audio_bitrate(file_path):
     process = [
        "ffprobe",
        "-v",
        "quiet",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=bit_rate",
        "-of",
        "json",
        file_path,
     ]

     output = subprocess.check_output(process)
     data = json.loads(output)

     if "streams" in data and len(data["streams"]) > 0 : 
          bitrate = data["streams"][0].get("bit_rate")
          return round(float(bitrate) / 1000) if bitrate else 0
     
     return 0


def detect_gpu_encoder():
        try:
            cmd = ["ffmpeg", "-hide_banner", "-encoders"]
            output = subprocess.check_output(cmd, universal_newlines=True)

            if "hevc_nvenc" in output:
                return "hevc_nvenc"
            elif "hevc_qsv" in output:  # Intel QuickSync
                return "hevc_qsv"
            elif "hevc_amf" in output:  # AMD
                return "hevc_amf"
            else:
                return None

        except subprocess.CalledProcessError:
            return None
        
def get_resolution_label(video_path):
     clip = VideoFileClip(video_path)
     width, height = clip.size
     clip.close()

    
     if width>=2560 or height>=1440:
          return "high res"
     else:
          return "accepted"