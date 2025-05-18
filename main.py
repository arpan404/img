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
    parser.add_argument(
        "--speed",
        type=float,
        default=0.8,
        help="Playback speed (0.5=half speed, 1.0=normal)"
    )
    parser.add_argument(
        "--voice",
        choices=["default", "morgan", "emma"],
        default="default",
        help="Choose a 'celebrity' voice"
    )
    args = parser.parse_args()

    config = Config("config.json")
    config.load()
    img = Img(
        ref_wav=args.ref,
        speed=args.speed,
        voice=args.voice,
    )
    # drive a fresh Gemini‐generated story from the "style1" prompt
    img.generate(config=config.get_style("style1"))


if __name__ == "__main__":
    main()
