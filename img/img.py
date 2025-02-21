import os
from google import genai
import re
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
import random
from img.types import Styles, Stories
import uuid
import soundfile as sf
import numpy as np
from gtts import gTTS
from pydub import AudioSegment
import numpy as np
import scipy.io.wavfile as wav
import noisereduce as nr
from pydub.effects import normalize, high_pass_filter, low_pass_filter


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
                video_path = os.path.join(
                    os.getcwd(), "videos", self.__content_config.video
                )
        # check if path exists and is a file
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            raise Exception("Video file does not exist")

        # if path is valid, set it in the content style
        self.__content_config.video = video_path

    def __check_create_temp_dir(self, folder: str = "temp") -> None:
        if not os.path.exists(os.path.join(os.getcwd(), folder)):
            os.makedirs(os.path.join(os.getcwd(), folder))

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

        composite_data = [edited_clip]
        texts = self.__story.split(" ")
        text_group = ""
        group_size = 0
        start_time = 0
        #todo: make this sync with voice
        text_max_sizes = (5, 50)  # 5 words maximum, 100 characters maximum
        for index, text in enumerate(texts):
            if (
                group_size + 1 > text_max_sizes[0]
                or len(text_group) + len(text) + 1 > text_max_sizes[1] or index == len(texts) - 1
            ):
                text_duration = len(text_group) * 0.1 + text_group.count(".") * 0.5 + text_group.count(",") * 0.2
                text_group = text_group + " " + text
                text_clip = TextClip(
                    text=text_group.strip(),
                    font_size=40,
                    color="white",
                    margin=(10, 20),
                    font="Arial",
                    method="caption",
                    size=(video_width - 80, None),
                )
                text_clip = text_clip.with_duration(text_duration)
                text_clip = text_clip.with_start(start_time)
                text_clip = text_clip.with_position("center").with_fps(video.fps)
                composite_data.append(text_clip)
                text_group = ""
                group_size = 0
                start_time += text_duration
            else:
                text_group = text_group + " " + text
                group_size += 1

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
        print(self.__story)
        self.__story = re.sub(r"[^a-zA-Z0-9.?',!\s]", "", self.__story)
        print(self.__story)

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
        self.__modify_audio()

    def __modify_audio(self) -> None:
        """
        Modify the audio like pitch, speed, etc.
        """

        audio = AudioSegment.from_file(self.__audio_path)

        louder_audio = audio + 12
        faster_audio = louder_audio.speedup(playback_speed=1.1)

        filtered_audio = high_pass_filter(faster_audio, 50)
        filtered_audio = low_pass_filter(filtered_audio, 5000)

        processed_audio = normalize(filtered_audio)

        temp_wav_path = self.__audio_path.replace(".wav", "_temp.wav")
        processed_audio.export(temp_wav_path, format="wav")

        rate, data = wav.read(temp_wav_path)

        cleaned_data = nr.reduce_noise(y=data, sr=rate)

        wav.write(self.__audio_path, rate, cleaned_data)

        # Remove temporary file
        os.remove(temp_wav_path)

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
        self.__generate_video()
