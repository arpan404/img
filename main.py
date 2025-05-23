import os

from dotenv import load_dotenv

load_dotenv()

from img.tts import text_to_speech, remove_silence
from img.story import generate_story
from img import Config
from img.types import Configuration, Styles
from img.video import __download_video

cf = Config()
style = cf.get_style("style1")
story = generate_story(style.prompt)
# __download_video("https://www.youtube.com/watch?v=89oSfqr7xWw")  
out = os.path.join(os.getcwd(), "audio-out", "output.mp3")
text_to_speech(story, out)
#remove_silence(out,out)