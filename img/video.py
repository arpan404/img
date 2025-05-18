import os
from pytube import YouTube

temp_dir = os.path.join(os.getcwd(), "temp")

def __download_video(url:str) -> str:
    yt = YouTube(url)
    video_uuid = yt.video_id
    video_filepath = os.path.join(temp_dir, "videos", f"{video_uuid}.mp4")

    if os.path.exists(video_filepath):
        return video_filepath

    # Create temp directory if it doesn't exist
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        os.makedirs(os.path.join(temp_dir, "videos"))
    
    if not os.path.exists(os.path.join(temp_dir, "videos")):
        os.makedirs(os.path.join(temp_dir, "videos"))
    
    stream_1080p = yt.streams.filter(res="1080p", progressive=True).first()
    if stream_1080p:
        stream_1080p.download(output_path=video_filepath)
        return video_filepath
    best_stream = yt.streams.filter(progressive=True).first()
    if best_stream:
        best_stream.download(output_path=video_filepath)
        return video_filepath
    raise Exception(f"Error downloading video: {yt.title} - {yt.video_id}")

def __validateVideoPath(filepath_in_config:str) -> str:
    if filepath_in_config.startswith("http"):
        return __download_video(filepath_in_config)
    # Check if the path is absolute or relative and convert to absolute path
    is_abs = os.path.isabs(filepath_in_config)
    if is_abs:
        video_path = filepath_in_config
    else:
        is_relative = os.path.isfile(filepath_in_config)
        if is_relative:
            video_path = os.path.join(os.getcwd(), filepath_in_config)
        else:
            default_folder = os.path.join(os.getcwd(), "temp", "videos")
            if not os.path.isdir(default_folder):
                raise Exception(f"Video directory does not exist: {default_folder}")
            video_path = os.path.join(default_folder, filepath_in_config)

    # return the absolute path
    if not os.path.exists(video_path) or not os.path.isfile(video_path):
        raise Exception("Video file does not exist")

    return video_path



def __get_video_path(filepath_in_config:str)->str:
    """
    
    """

    if not filepath_in_config.startswith("http"):
        return filepath_in_config
    

