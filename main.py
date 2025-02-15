from img.gemini import get_content
from img.filter import filter_content
from dotenv import load_dotenv
import pyttsx3
load_dotenv()

engine = pyttsx3.init()
a = get_content("""Create a gripping 50-60 second story that immediately captures attention with a shocking twist. It must be a story time.""")


voices = engine.getProperty('voices')
for index, voice in enumerate(voices):
    print(f"Index: {index}, ID: {voice.id}, Name: {voice.name}")

engine.setProperty('voice', voices[132].id)
# Adjust speech rate
engine.setProperty('rate', 150)
# Adjust volume (0.0 to 1.0)
engine.setProperty('volume', 1)
engine.say(a)
engine.runAndWait()
