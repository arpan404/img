import os
from google import genai
import uuid
import re
from moviepy import VideoFileClip, AudioFileClip
import random

class Img:

    def __init__(self, content_style, content_id):
        """
        content_style: dict
        content_id: str
        
        content_id is the id of the content to be generated.
        content_style is the style of the content to be generated, defined in config.json.
        """
        self.__content_id = content_id
        self.__content_style = content_style

        if not self.__content_style:
            raise Exception("No content style specified")
        
        if not self.__content_style["prompt"]:
            raise Exception("No prompt specified")

        self.__validateVideoPath()
       
    
    def __validateVideoPath(self):
        """
        Validates the video path specified in the content style.
        """

        if not self.__content_style["videoFile"]:
            raise Exception("No video file specified")
        
        is_abs = os.path.isabs(self.__content_style["videoFile"])

        # check if path is absolute or relative and convert to absolute path
        if is_abs:
            video_path = self.__content_style["videoFile"]
        else:
            is_relative = os.path.isfile(self.__content_style["videoFile"])
            if is_relative:
                video_path = os.path.join(os.getcwd(), self.__content_style["videoFile"])
            else:
                video_path = os.path.join(
                    os.getcwd(), "videos", self.__content_style["videoFile"]
                )
        # check if path exists and is a file
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            raise Exception("Video file does not exist")
        
        # if path is valid, set it in the content style
        self.__content_style["videoFile"] = video_path

    def __generate_video(self):
    
        video_path = self.__content_style["videoFile"]

        video = VideoFileClip(video_path)
        audio = AudioFileClip(self.__audio_path)

        if video.duration < audio.duration:
            raise Exception("Video duration is less than audio duration")

        video_height = video.h
        video_width = video.w

        # crop video to 16:9 aspect ratio (for short content)
        content_width = int(video_height * 9 / 16)

        if content_width> video_width:
            raise Exception("Video is not wide enough")
        
        # pixels needed to be cropped from left side
        crop_x1 = (video_width - content_width) / 2

        # pixels needed to be cropped from right side
        crop_x2 = video_width - crop_x1

        # random starting point for video, based on audio duration
        video_starting_point = random.uniform(0, video.duration - audio.duration)

        #  trim the video, then crop it, then add the audio (in this order for performance reasons)
        edited_clip = video.subclipped(
            video_starting_point, video_starting_point + self.__audio_duration
        ).without_audio().cropped(x1=crop_x1, x2=crop_x2).with_audio(audio)

        self.__edited_video_path = os.path.join(os.getcwd(), "temp", f"{self.__content_id}.mp4")

        edited_clip.write_videofile(self.__edited_video_path, codec="libx264", audio_codec="aac")