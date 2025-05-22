import os
import random
import re
import uuid
from pathlib import Path

from moviepy import AudioFileClip, CompositeVideoClip, TextClip, VideoFileClip
from img.types import Stories, Styles
from img.story import generate_story
from img.tts import text_to_audio

from pydub import AudioSegment   # ← added for concatenation

class Img:
    def __init__(self, ref_wav: str | None = None, speed: float = 0.1, voice: str = "default"):
        self.__content_id = str(uuid.uuid4())
        default_ref = Path(__file__).parent 
        self.ref_wav = str(ref_wav or default_ref)
        self.speed = speed
        self.voice = voice

    def __validateVideoPath(self) -> None:
        if not self.__content_config.video:
            raise Exception("No video file specified")

        is_abs = os.path.isabs(self.__content_config.video)

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

        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            raise Exception("Video file does not exist")

        self.__content_config.video = video_path

    def __check_create_temp_dir(self, folder: str = "temp") -> None:
        if not os.path.exists(os.path.join(os.getcwd(), folder)):
            os.makedirs(os.path.join(os.getcwd(), folder))

    def __generate_story(self) -> None:
        """
        Uses story.py to generate a story using OpenAI API instead of Gemini.
        """
        prompt = self.__content_config.prompt
        self.__story = generate_story(prompt)       # ✅ Use your story.py
        print("[Story Generated]", self.__story)

    def __generate_audio(self) -> None:
        """
        Generate four separate audio segments from the story, concatenate them,
        and set self.__audio_path to the merged file.
        """
        self.__check_create_temp_dir("temp")
        words = self.__story.split()
        total = len(words)

        # split into up to 4 chunks
        if total < 4:
            parts = [words]
        else:
            chunk = total // 4
            parts = [words[i*chunk:(i+1)*chunk] for i in range(3)]
            parts.append(words[3*chunk:])

        combined = AudioSegment.empty()
        for idx, chunk_words in enumerate(parts, start=1):
            txt = " ".join(chunk_words)
            part_fp = os.path.join(os.getcwd(), "temp", f"{self.__content_id}_part{idx}.mp3")
            text_to_audio(txt, part_fp)                   # synthesize part
            combined += AudioSegment.from_file(part_fp)   # append to combined

        final_fp = os.path.join(os.getcwd(), "temp", f"{self.__content_id}.mp3")
        combined.export(final_fp, format="mp3")
        self.__audio_path = final_fp

    def __generate_video(self) -> None:
        video = VideoFileClip(self.__content_config.video)
        audio = AudioFileClip(self.__audio_path)

        if video.duration < audio.duration:
            raise Exception("Video duration is less than audio duration")

        video_height = video.h
        video_width = video.w
        content_width = int(video_height * 9 / 16)

        if content_width > video_width:
            raise Exception("Video is not wide enough")

        crop_x1 = (video_width - content_width) / 2
        crop_x2 = video_width - crop_x1
        video_starting_point = random.uniform(0, video.duration - audio.duration)

        edited_clip = (
            video.subclipped(video_starting_point, video_starting_point + audio.duration) # Corrected from subclip to subclipped
            .without_audio()
            .cropped(x1=crop_x1, x2=crop_x2)
            .with_audio(audio)
        )

        composite_data = [edited_clip]
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

        edited_clip = CompositeVideoClip(composite_data)
        self.__check_create_temp_dir("output")
        self.__edited_video_path = os.path.join(os.getcwd(), "output", f"{self.__content_id}.mp4")
        edited_clip.write_videofile(self.__edited_video_path, codec="libx264", audio_codec="aac")
        os.remove(self.__audio_path)

    def generate(self, config: Styles | Stories) -> None:
        self.__content_config = config
        self.__validateVideoPath()

        if isinstance(config, Stories):
            self.__story = config.story
        else:
            self.__generate_story()    # ✅ Uses story.py

        self.__generate_audio()        # ✅ Uses tts.py
        self.__generate_video()
