import os
import subprocess,json
from pathlib import Path
from moviepy import VideoFileClip

def calculate_video_bitrate(file_path, target_size_mb):
    clip = VideoFileClip(file_path)
    v_len = clip.duration
    clip.close()
    print(f"Video duration: {v_len} seconds")
    a_rate = get_audio_bitrate(file_path)
    print(f"Audio Bitrate: {a_rate}k")
    total_bitrate = (target_size_mb * 8192.0 * 0.98) / (1.048576 * v_len) - a_rate
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

            if "av1_nvenc" in output:
                return "av1_nvenc"
            elif "av1_qsv" in output:  # Intel QuickSync
                return "av1_qsv"
            elif "av1_amf" in output:  # AMD
                return "av1_amf"
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
     
def compress(file,target_file_size,encoder = detect_gpu_encoder()):
    file = Path(file)
    size = (os.path.getsize(file)/1000)/1000
    output_path = os.path.join(file.parent,"compressed")
    
    if not os.path.isdir(output_path):
         os.mkdir(output_path)

    output_path = os.path.join(output_path, file.stem+"_compressed.mp4")

    

    if size>2000:
         
        print("compressing - "+file.name+"...")
        expected_bitrate = calculate_video_bitrate(file,float(target_file_size))
        cmd_args = ["ffmpeg", "-i" , str(file)]
         
        if get_resolution_label(file)=="high res":
            cmd_args.append(["-vf","scale=1920:1080"])

        process_args_pass_1 =cmd_args + [
              "-b:v", str(expected_bitrate)+"k",
              "-c:v", encoder, 
              "-pass", "1",
              "-an", #meaning audio off
              "-f",
              "mp4",
              "TEMP" # this means output won't be saved

         ]
        print(process_args_pass_1)
        process_args_pass_2 = cmd_args + [
              "-b:v", str(expected_bitrate)+"k",
              "-c:v", encoder,
              "-pass", "2",
              "-c:a", "copy",
              str(output_path)
        ]

        subprocess.run(process_args_pass_1)
        subprocess.run(process_args_pass_2)


    else:
        cmd_args = ["ffmpeg", "-i" , str(file)]
        
        if get_resolution_label(file)=="high res":
            cmd_args.append(["-vf","scale=1920:1080"])
        
        process_args = cmd_args + [
              "-c:v", encoder,
              "-crf", "20",
              "-b:v", "0",
              "-c:a", "copy",
              str(output_path)
        ]

        subprocess.run(process_args)
    
    

         