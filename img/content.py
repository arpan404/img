import os
from google import genai
import uuid
import re
from gtts import gTTS
from pydub import AudioSegment
from moviepy import VideoFileClip, AudioFileClip
import random


class Content:
    def __generate_audio(self, text: str) -> str | None:
        """
        Returns the path of the audio file generated by gtts or None if an error occurs.
        """
        try:
            if not os.path.exists(os.path.join(os.getcwd(), "temp")):
                os.mkdir(os.path.join(os.getcwd(), "temp"))

            audio_path = os.path.join(os.getcwd(), "temp", f"{self.__content_id}.mp3")
            tts = gTTS(text=text, lang="en")
            tts.save(audio_path)
            return audio_path
        except Exception as e:
            print(e)
            return None

    def __speed_up_audio(
        self, input_path: str, output_path: str, speed: float = 1.5
    ) -> bool:
        """
        Speeds up the audio file using pydub.
        """
        try:
            audio = AudioSegment.from_file(input_path)
            sped_up_audio = audio.speedup(playback_speed=speed)
            sped_up_audio.export(output_path, format="mp3")
            return sped_up_audio.duration_seconds
        except Exception as e:
            print(e)
            return False

    def __generate_video(self):
        if not self.__style["videoFile"]:
            raise Exception("No video file specified")
        is_abs = os.path.isabs(self.__style["videoFile"])
        if is_abs:
            video_path = self.__style["videoFile"]
        else:
            is_relative = os.path.isfile(self.__style["videoFile"])
            if is_relative:
                video_path = os.path.join(os.getcwd(), self.__style["videoFile"])
            else:
                video_path = os.path.join(
                    os.getcwd(), "videos", self.__style["videoFile"]
                )
        print(video_path)
        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            raise Exception("Video file does not exist")

        video = VideoFileClip(video_path)
        video_duration = video.duration
        if video_duration < self.__audio_duration:
            raise Exception("Video is shorter than audio")
        video_starting_point = random.uniform(0, video_duration - self.__audio_duration)
        edited_video = video.subclipped(
            video_starting_point, video_starting_point + self.__audio_duration
        ).without_audio()

        video_audio = AudioFileClip(self.__audio_path)
        edited_video = edited_video.without_audio().with_audio(video_audio)
        edited_video.write_videofile(
            os.path.join(os.getcwd(), "temp", f"{self.__content_id}_trimmed.mp4"),
            codec="libx264",
            audio_codec="aac",
        )

    def __generate_story(self, prompt: str):
        """
        Returns the content (story) generated by Gemini or None if an error occurs.
        """
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash-001", contents=prompt
            )
            self.__story = re.sub(r"\(.*?\)", "", response.text)
            return response.text

        except Exception as e:
            print(e)

    def generate(self, style: dict) -> str | None:
        self.__content_id = str(uuid.uuid4())
        self.__style = style
        self.__audio__speed = 1.25
        self.__generate_story(style["prompt"])
        generated_audio_path = self.__generate_audio(self.__story)
        if generated_audio_path is None:
            print("Error generating audio")
            raise Exception("Error generating audio")
        sped_up_audio_path = os.path.join(
            os.getcwd(), "temp", f"{self.__content_id}_sped_up.mp3"
        )
        self.__audio_path = sped_up_audio_path
        self.__audio_duration = self.__speed_up_audio(
            generated_audio_path, sped_up_audio_path
        )
        if self.__audio_duration is False:
            print("Error speeding up audio")
            raise Exception("Error speeding up audio")
        self.__generate_video()
