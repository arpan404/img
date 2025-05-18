import os
os.environ["LLM_API_KEY"] = "AIzaSyDXvcK1e8yWG0A6UJxoydKYLk8az3CIG-Y"
os.environ["LLM_API_URL"] = "https://generativelanguage.googleapis.com/v1beta/openai/"
os.environ["LLM_MODEL_NAME"] = "gemini-2.0-flash"
from img.config import Config
from img.img import Img
from img.story import generate_story

def main():
    # load and parse config
    cfg = Config(os.path.join(os.getcwd(), "config.json"))
    cfg.load()

    # fetch style (has prompt, video, language)
    style_obj = cfg.get_style("style1")

    # generate story text (optional, Img.generate will also do this if you skip this step)
    story_text = generate_story(prompt=style_obj.prompt)

    # run the full Img pipeline (TTS + video edit)
    img = Img()
    img.generate(style_obj)

if __name__ == "__main__":
    main()
