from dia.model import Dia
from img.story import generate_story
import os
import torchaudio

def text_to_audio(
    story_text: str,
    output_dir: str = "output",
):
    """
    Generate separate audio files for each [S1]/[S2] line using two distinct voices.
    """
    model = Dia.from_pretrained("nari-labs/Dia-1.6B", compute_dtype="float16")
    os.makedirs(output_dir, exist_ok=True)

    paths = []
    s1_count = 0
    s2_count = 0

   # split and ensure both S1/S2 appear
    lines = story_text.splitlines()
    if not any(l.startswith("[S2]") for l in lines):
        new = []
        for i, l in enumerate(lines):
            # strip existing tag if present
            body = l.partition("]")[2].strip() if l.startswith("[S") else l.strip()
            tag  = "[S1]" if i % 2 == 0 else "[S2]"
            new.append(f"{tag} {body}")
        lines = new

    for line in lines:
        if line.startswith("[S1]"):
            s1_count += 1
            text = line.partition("]")[2].strip()
            clone_from_audio = "/Users/rijan/img/img/peter-audio.mp3"

            # --- convert clone to mono WAV ---
            wav, sr = torchaudio.load(clone_from_audio)
            if wav.size(0) > 1:
                wav = wav.mean(dim=0, keepdim=True)
            tmp = os.path.join(output_dir, f"clone_s1_{s1_count}.wav")
            torchaudio.save(tmp, wav, sr)

            # --- generate & save ---
            audio = model.generate(text, audio_prompt=tmp, use_torch_compile=False, verbose=True)
            out = os.path.join(output_dir, f"s1_{s1_count}.mp3")
            model.save_audio(out, audio)
            paths.append(out)
            os.remove(tmp)

        elif line.startswith("[S2]"):
            s2_count += 1
            text = line.partition("]")[2].strip()
            clone_from_audio = "/Users/rijan/img/img/louis_griffin.mp3"

            # --- convert clone to mono WAV ---
            wav, sr = torchaudio.load(clone_from_audio)
            if wav.size(0) > 1:
                wav = wav.mean(dim=0, keepdim=True)
            tmp = os.path.join(output_dir, f"clone_s2_{s2_count}.wav")
            torchaudio.save(tmp, wav, sr)

            # --- generate & save ---
            audio = model.generate(text, audio_prompt=tmp, use_torch_compile=False, verbose=True)
            out = os.path.join(output_dir, f"s2_{s2_count}.mp3")
            model.save_audio(out, audio)
            paths.append(out)
            os.remove(tmp)

        else:
            continue

    return paths
