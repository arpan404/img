import argparse
import soundfile as sf
from dia.model import Dia

# reusable synth function
def synthesize(text: str, out_path: str, sr: int = 44100) -> None:
    """
    Generate waveform for `text` and write to `out_path`.
    """
    model = Dia.from_pretrained("nari-labs/Dia-1.6B")
    waveform = model.generate(text)
    sf.write(out_path, waveform, sr)

def main():
    parser = argparse.ArgumentParser(
        description="Convert text (or file) to speech using Dia TTS"
    )
    parser.add_argument("-t", "--text", help="Text string to synthesize")
    parser.add_argument("-f", "--file", help="Path to .txt file with text")
    parser.add_argument(
        "-o", "--output", default="speech.mp3", help="Output audio file path"
    )
    args = parser.parse_args()

    if args.text:
        text = args.text
    elif args.file:
        with open(args.file, "r") as rf:
            text = rf.read()
    else:
        parser.error("Provide either --text or --file")

    synthesize(text, args.output)
    print(f"✓ Speech saved to {args.output}")

if __name__ == "__main__":
    main()
