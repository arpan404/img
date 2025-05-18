import os
from pytube import YouTube


def __download_video(url:str) -> str:
    """
    Downloads a video from the given URL and saves it to a temporary directory.
    If the video is already downloaded, it returns the path to the existing file.

    :param url: The URL of the video to download.
    :return: The path to the downloaded video file.
    """
    temp_dir = os.path.join(os.getcwd(), "temp")
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
    
    stream_1080p = yt.streams.filter(res="1080p", progressive=True).first() # priotize 1080p else fallback to the best stream
    if stream_1080p:
        stream_1080p.download(output_path=video_filepath)
        return video_filepath
    
    best_stream = yt.streams.filter(progressive=True).first()
    if best_stream:
        best_stream.download(output_path=video_filepath)
        return video_filepath
    raise Exception(f"Error downloading video: {yt.title} - {yt.video_id}")

def __validateVideoPath(filepath_in_config:str) -> str:
    """
    Validates the video path specified in the style in the config.
    Will check if the path provided is a URL or a local file path.
    If it is a URL, it will download the video and return the path to the downloaded file.
    If it is a local file path, it will check if the file exists and return the absolute path.
    Will raise an exception if the video file does not exist.

    :param filepath_in_config: The path to the video file.
    :return: The absolute path to the video file.
    """
    assert filepath_in_config, "No video file specified"

    if filepath_in_config.startswith("http"):
        video_path =__download_video(filepath_in_config)
        if not os.path.exists(video_path):
            raise Exception(f"Video file does not exist: {video_path}")
        return video_path

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
