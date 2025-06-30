import subprocess,os
from moviepy import VideoFileClip

def extract_thumbnail(video_path, thumb_path='thumb.jpg'):
    cmd = [
        'ffmpeg', '-ss' , '00:00:02', '-i', video_path,
        '-frames:v', '1', '-q:v', '2', thumb_path, '-y'
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return thumb_path

def get_video_metadata(path):
        clip = VideoFileClip(path)
        duration = int(clip.duration)
        width = clip.w 
        height = clip.h
        clip.close()
        return duration, width , height

def is_media(file_path):
        
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

def is_video(file_path):
    
    video_extensions = [
        ".3g2", ".3gp", ".amv", ".asf", ".avi", ".bik", ".clpi", ".divx", ".drc", ".dv", ".dvb",
        ".evo", ".f4p", ".f4v", ".flc", ".fli", ".flic", ".flv", ".gvi", ".gxf", ".h264", ".h265",
        ".iso", ".m1v", ".m2p", ".m2t", ".m2ts", ".m2v", ".m4v", ".mkv", ".mod", ".mov", ".mp2",
        ".mp2v", ".mp4", ".mp4v", ".mpe", ".mpeg", ".mpg", ".mpv", ".mqv", ".mts", ".mxf", ".nsv",
        ".nut", ".ogg", ".ogm", ".ogv", ".qt", ".rm", ".rmvb", ".roq", ".rpl", ".thp", ".tod",
        ".tp", ".trp", ".ts", ".vob", ".vro", ".webm", ".wm", ".wmv", ".wtv", ".yuv"
    ]

    if file_path.suffix.lower() in video_extensions:
         return True
    
    return False

def is_old_video(file_path):
    old_video_extensions = [
        ".3gp", ".amv", ".asf", ".avi", ".divx", ".dv",
        ".flv", ".fli", ".flic", ".gvi", ".mov", ".mpeg",
        ".mpg", ".mpv", ".nsv", ".ogv", ".qt", ".rm",
        ".rmvb", ".vob", ".wm", ".wmv", ".yuv"
    ]
     
    if file_path.suffix.lower() in old_video_extensions:
         return True
    
    return False
    
