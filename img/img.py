import os
from google import genai
import re
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip
import random
from img.types import Styles, Stories
import uuid
import json

class Img:

    def __init__(self):
        """
        Initializes the Img class. Will generate a unique content id for the content.
        """
        self.__content_id = str(uuid.uuid4())

    def __validateVideoPath(self) -> None:
        """

        Validates the video path specified in the content style.
        Will check the value inside self.__content_config.video and convert it to an absolute path if it is not already.

        Will raise an exception if the video file does not exist.
        """
        print(self.__content_config)
        if not self.__content_config.video:
            raise Exception("No video file specified")

        is_abs = os.path.isabs(self.__content_config.video)

        # check if path is absolute or relative and convert to absolute path
        if is_abs:
            video_path = self.__content_config.video
        else:
            is_relative = os.path.isfile(self.__content_config.video)
            if is_relative:
                video_path = os.path.join(
                    os.getcwd(), self.__content_config.video
                )
            else:
                video_path = os.path.join(
                    os.getcwd(), "videos", self.__content_config.video
                )
        # check if path exists and is a file
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            raise Exception("Video file does not exist")

        # if path is valid, set it in the content style
        self.__content_config.video = video_path

    def __check_create_temp_dir(self) -> None:
        if not os.path.exists(os.path.join(os.getcwd(), "temp")):
            os.makedirs(os.path.join(os.getcwd(), "temp"))

    def __generate_video(self) -> None:

        video_path = self.__content_config.video

        video = VideoFileClip(video_path)
        audio = AudioFileClip(self.__audio_path)

        if video.duration < audio.duration:
            raise Exception("Video duration is less than audio duration")

        video_height = video.h
        video_width = video.w

        # crop video to 16:9 aspect ratio (for short content)
        content_width = int(video_height * 9 / 16)

        if content_width > video_width:
            raise Exception("Video is not wide enough")

        # pixels needed to be cropped from left side
        crop_x1 = (video_width - content_width) / 2

        # pixels needed to be cropped from right side
        crop_x2 = video_width - crop_x1

        # random starting point for video, based on audio duration
        video_starting_point = random.uniform(0, video.duration - audio.duration)

        #  trim the video, then crop it, then add the audio (in this order for performance reasons)
        edited_clip = (
            video.subclipped(
                video_starting_point, video_starting_point + audio.duration
            )
            .without_audio()
            .cropped(x1=crop_x1, x2=crop_x2)
            .with_audio(audio)
        )

        self.__check_create_temp_dir()

        # path to save the edited video
        self.__edited_video_path = os.path.join(
            os.getcwd(), "temp", f"{self.__content_id}.mp4"
        )

        edited_clip.write_videofile(
            self.__edited_video_path, codec="libx264", audio_codec="aac"
        )

    def __generate_story(self) -> None:
        """

        Generate a story based on the prompt specified in the content style, and set it to self.__story.
        Will use google Gemini 2.0 flash as LLM

        Will raise an exception if the story generation fails.

        """
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash-001", contents=self.__content_config.prompt
        )

        # remove any text inside parentheses from the story (usually it contains the environment description, which is not needed)
        self.__story = re.sub(r"\(.*?\)", "", response.text)

    def __generate_audio(self) -> None:
        """
        Generate audio based on the story and the voice specified in the content style.

        Will raise an exception if the audio generation fails.
        """

        # todo: make this voice thing more natural
        tts = gTTS(text=self.__story, lang=self.__content_config.language)
        self.__check_create_temp_dir()
        self.__audio_path = os.path.join(
            os.getcwd(), "temp", f"{self.__content_id}.wav"
        )
        tts.save(self.__audio_path)

    def generate(self, config: Styles | Stories) -> None:
        """
        Generate content based on the config provided.
        Will raise an exception if the content generation fails.

        Will not handle any errors, so make sure to handle them in the caller function.
        """
        self.__content_config = config  

        # validate the video path before starting the generation process
        self.__validateVideoPath()

        if(self.__content_config.story):
            self.__story = self.__content_config.story
        else:
            self.__generate_story()

        self.__generate_audio()
        self.__generate_video()
        