import os
import random
import re
import uuid
from pathlib import Path

from google import genai
from moviepy import AudioFileClip, CompositeVideoClip, TextClip, VideoFileClip
from pydub import AudioSegment
from pydub.effects import normalize

from img.tts import synthesize  # use our TTS helper
from img.types import Stories, Styles


class Img:

    def __init__(
        self,
        ref_wav: str | None = None,
        speed: float = 0.8,
        voice: str = "default",
    ):
        """
        Initializes the Img class. Will generate a unique content id for the content.
        """
        self.__content_id = str(uuid.uuid4())
        # default to local videoplayback.wav
        default_ref = Path(__file__).parent / "videoplayback.wav"
        self.ref_wav = str(ref_wav or default_ref)
        self.speed = speed
        self.voice = voice

    def __validateVideoPath(self) -> None:
        """

        Validates the video path specified in the content style.
        Will check the value inside self.__content_config.video and convert it to an absolute path if it is not already.

        Will raise an exception if the video file does not exist.
        """

        if not self.__content_config.video:
            raise Exception("No video file specified")

        is_abs = os.path.isabs(self.__content_config.video)

        # check if path is absolute or relative and convert to absolute path
        if is_abs:
            video_path = self.__content_config.video
        else:
            is_relative = os.path.isfile(self.__content_config.video)
            if is_relative:
                video_path = os.path.join(os.getcwd(), self.__content_config.video)
            else:
                default_folder = os.path.join(os.getcwd(), "img", "videos")
                if not os.path.isdir(default_folder):
                    raise Exception(f"Video directory does not exist: {default_folder}")
                video_path = os.path.join(default_folder, self.__content_config.video)
        # check if path exists and is a file
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            raise Exception("Video file does not exist")

        # if path is valid, set it in the content style
        self.__content_config.video = video_path

    def __check_create_temp_dir(self, folder: str = "temp") -> None:
        if not os.path.exists(os.path.join(os.getcwd(), folder)):
            os.makedirs(os.path.join(os.getcwd(), folder))

    def __generate_video(self) -> None:

        video = VideoFileClip(self.__content_config.video)
        # audio was generated at 0.8× speed in synthesize()
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

        composite_data = [edited_clip]
        # smooth captions: split into words and assign equal chunks of audio.duration
        words = self.__story.split()
        if words:
            dur = audio.duration / len(words)
            for idx, w in enumerate(words):
                txt = TextClip(
                    text=w,
                    font_size=40,
                    color="white",
                    margin=(10, 20),
                    font="Arial",
                    method="caption",
                    size=(video_width - 80, None),
                ).with_start(idx * dur).with_duration(dur) \
                 .with_position("center").with_fps(video.fps)
                composite_data.append(txt)

        # Combine the video and the text clips
        edited_clip = CompositeVideoClip(composite_data)

        self.__check_create_temp_dir()

        # path to save the edited video
        self.__edited_video_path = os.path.join(
            os.getcwd(), "output", f"{self.__content_id}.mp4"
        )
        self.__check_create_temp_dir("output")
        edited_clip.write_videofile(
            self.__edited_video_path, codec="libx264", audio_codec="aac"
        )
        os.remove(self.__audio_path)


    def generate(self, config: Styles | Stories) -> None:
        """
        Generate content based on the config provided.
        Will raise an exception if the content generation fails.

        Will not handle any errors, so make sure to handle them in the caller function.
        """
        self.__content_config = config

        # validate the video path before starting the generation process
        self.__validateVideoPath()

        if isinstance(self.__content_config, Stories):
            self.__story = self.__content_config.story
        else:
            self.__generate_story()

        self.__generate_audio()
        self.__modify_audio()
        self.__generate_video()
