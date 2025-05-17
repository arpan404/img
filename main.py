import argparse
import os
from img.config import Config
from img.img import Img


def main():
    parser = argparse.ArgumentParser(
        description="Generate video content with TTS"
    )
    parser.add_argument(
        "--ref",
        help="Path to reference WAV for voice style",
        default=os.path.join("img", "videoplayback.wav")
    )
    args = parser.parse_args()

    config = Config("config.json")
    config.load()
    img = Img(ref_wav=args.ref)
    # drive a fresh Gemini‐generated story from the "style1" prompt
    img.generate(config=config.get_style("style1"))


if __name__ == "__main__":
    main()
