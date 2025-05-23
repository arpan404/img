"""
This module is responsible for downloading a video from a URL or local path,
cropping it to a 16:9 aspect ratio, and adding audio to the video.
It uses the moviepy library for video editing and pytubefix for downloading YouTube videos.
"""

import os
import random
from typing import List

from moviepy import AudioFileClip, CompositeVideoClip, TextClip, VideoFileClip
from pytubefix import YouTube


def __download_video(url: str) -> str:
    """
    Downloads a video from the given URL and saves it to a temporary directory.
    If the video is already downloaded, it returns the path to the existing file.

    :param url: The URL of the video to download.
    :return: The path to the downloaded video file.
    """
    temp_dir = os.path.join(os.getcwd(), "temp")
    yt = YouTube(url)
    video_uuid = yt.video_id
    video_folder_path = os.path.join(temp_dir, "videos")
    stream = (
        yt.streams.filter(res="1080p").first()
        if yt.streams.filter(res="1080p").first()
        else yt.streams.get_highest_resolution()
    )
    video_file_name = f"{video_uuid}.{stream.mime_type.split('/')[1]}"
    video_file_path = os.path.join(video_folder_path, video_file_name)

    if os.path.exists(video_file_path):
        return video_file_path

    # Create temp directory if it doesn't exist
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        os.makedirs(video_folder_path)

    if not os.path.exists(video_folder_path):
        os.makedirs(video_folder_path)

    if stream:
        stream.download(output_path=video_folder_path, filename=video_file_name)
        return video_file_path

    raise Exception(f"Error downloading video: {yt.title} - {yt.video_id}")


def validateVideoPath(filepath_in_config: str) -> str:
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
        video_path = __download_video(filepath_in_config)
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


def __get_caption_data(caption: str, audio_file: str) -> List[TextClip]:
    text_clips = []
    for i in range(0, 10):
        txt = TextClip(
            text=f"CUrrent text is {i}", font_size=70, color="green", font="Arial"
        )
        txt = txt.with_position((random.randint(0, 100), random.randint(0, 100)))
        txt = txt.with_duration(2)
        txt = txt.with_start(i * 2)
        text_clips.append(txt)
    return text_clips


def generate_video(
    base_video_filepath: str, voice_over: str, caption: str, output_path: str
):
    """ """
    video = VideoFileClip(base_video_filepath)
    audio = AudioFileClip(voice_over)

    if video.duration < audio.duration:
        raise Exception("Video duration is less than audio duration")

    video_width = video.w
    video_height = video.h

    # crop the video to 16:9 aspect ratio
    content_width = int(video_height * (9 / 16))

    if content_width > video_width:
        raise Exception("Video width is less than content width")

    # pixels to crop from the left and right
    left_crop = (video_width - content_width) / 2
    right_crop = video_width - left_crop

    # random starting point for video, based on audio duration
    video_starting_point = random.uniform(0, video.duration - audio.duration)

    #  trim the video, then crop it, then add the audio (in this order for performance reasons)
    edited_clip = (
        video.subclipped(video_starting_point, video_starting_point + audio.duration)
        .without_audio()
        .cropped(x1=left_crop, x2=right_crop)
        .with_audio(audio)
    )
    caption_data = __get_caption_data(caption, voice_over)
    edited_clip = CompositeVideoClip([edited_clip] + caption_data)

    edited_clip.write_videofile(
        output_path,
        codec="h264_videotoolbox",
        audio_codec="aac",
        threads=os.cpu_count(),
        preset="ultrafast",
    )
    video.close()
    audio.close()
    edited_clip.close()
