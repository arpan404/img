import os
from img import Config, tts, generate_story

cf = Config()
style = cf.get_style("style1")
story = generate_story(style.prompt)
# __download_video("https://www.youtube.com/watch?v=89oSfqr7xWw")
out = os.path.join(os.getcwd(), "audio-out", "output.mp3")
tts(story, out)
# remove_silence(out,out)
