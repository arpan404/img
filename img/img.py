import os
import re
import uuid
import random
from pathlib import Path
from google import genai
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from pydub import AudioSegment
from pydub.effects import normalize
from img.types import Styles, Stories
from img.tts import synthesize    # use our TTS helper

class Img:

    def __init__(self, ref_wav: str | None = None):
        """
        Initializes the Img class. Will generate a unique content id for the content.
        """
        self.__content_id = str(uuid.uuid4())
        # default to local videoplayback.wav
        default_ref = Path(__file__).parent / "videoplayback.wav"
        self.ref_wav = str(ref_wav or default_ref)

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
        texts = self.__story.split(" ")
        total_words = len(texts)
        max_words_per_caption = 5
        text_group = ""
        group_size = 0
        start_time = 0

        for index, word in enumerate(texts):
            # add word first so segment_words includes it
            text_group += " " + word
            segment_words = text_group.strip().split()
            # break caption every N words or at end
            if (group_size + 1 > max_words_per_caption) or index == total_words - 1:
                # base duration proportional to segment length
                base = (len(segment_words) / total_words) * audio.duration
                # extra pause: 0.1s per comma, 0.3s per full-stop
                extra = segment_words.count(',') * 0.1 + segment_words.count('.') * 0.3
                text_duration = base + extra
                text_clip = TextClip(
                    text=text_group.strip(),
                    font_size=40,
                    color="white",
                    margin=(10, 20),
                    font="Arial",
                    method="caption",
                    size=(video_width - 80, None),
                )
                text_clip = text_clip.with_duration(text_duration).with_start(start_time)
                text_clip = text_clip.with_position("center").with_fps(video.fps)
                composite_data.append(text_clip)
                # reset for next segment
                text_group = ""
                group_size = 0
                start_time += text_duration
            else:
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
        Will use Google Gemini 2.0 flash as LLM
        """
        api_key = os.getenv("GEMINI_API_KEY")
        # export as GOOGLE_API_KEY so genai.Client() picks it up
        os.environ["GOOGLE_API_KEY"] = api_key
        client = genai.Client()

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
        Generate audio wav via Dia TTS, cloning style if voice_ref provided.
        """
        self.__check_create_temp_dir()
        out = os.path.join(os.getcwd(), "temp", f"{self.__content_id}.wav")
        synthesize(self.__story, out, speed=0.8, ref_wav=self.ref_wav)
        self.__audio_path = out

    def __modify_audio(self) -> None:
        """
        Lightly normalize audio to preserve the cloned voice characteristics.
        """
        audio = AudioSegment.from_file(self.__audio_path)
        normalized = normalize(audio)
        normalized.export(self.__audio_path, format="wav")

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
