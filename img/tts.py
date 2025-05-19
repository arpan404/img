from dia.model import Dia
from img.story import generate_story

def text_to_audio(story_text: str, output_path="output.mp3"):
    model = Dia.from_pretrained("nari-labs/Dia-1.6B", compute_dtype="float16")
    audio = model.generate(story_text, use_torch_compile=False, verbose=True)
    model.save_audio(output_path, audio)
    print(f"Audio saved to {output_path}")



