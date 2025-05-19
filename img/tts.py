import os
from dia.model import Dia
import tempfile
from typing import List
from pydub import AudioSegment

def text_to_speech(
    text:str,
    output_file:str,
):
    """
    Generate speech from text using Dia-1.6B model.
    """
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)
    s1_audio = os.path.join(os.getcwd(), "audio", "s1.mp3")
    s2_audio = os.path.join(os.getcwd(), "audio", "s2.mp3")

    if not os.path.exists(s1_audio) or not os.path.exists(s2_audio):
        raise FileNotFoundError(f"Audio file not found: {s1_audio if not os.path.exists(s1_audio) else s2_audio}")
    
    audio_temp_dir = tempfile.mkdtemp()
    model = Dia.from_pretrained("nari-labs/Dia-1.6B", compute_dtype="float16")
    transcripts = []
    last_line = ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("[S1]") or line.startswith("[S2]"):
            if len(last_line) > 0:
                transcripts.append(last_line)
                last_line = ""
            last_line += line
            last_line = last_line.strip()

    if len(last_line) > 0:
        transcripts.append(last_line)
    if len(transcripts) == 0:
        raise ValueError("No valid transcripts found in the text.")
    
    for i, transcript in enumerate(transcripts):
        speaker = "S1" if transcript.startswith("[S1]") else "S2"
        transcript = transcript.replace(f"[{speaker}]", "[S1]").strip()
        audio = model.generate(
            transcript,
            audio_prompt=s1_audio if speaker == "S1" else s2_audio,
            use_torch_compile=False,
            verbose=True,
        )
        out = os.path.join(audio_temp_dir, f"{speaker}_{i}.mp3")
        model.save_audio(out, audio)
        transcripts[i] = out
    
    # Combine audio files into a single output file
    with open(output_file, "wb") as outfile:
        for transcript in transcripts:
            with open(transcript, "rb") as infile:
                outfile.write(infile.read())
    output_audio = AudioSegment.empty()
    for audio in transcripts:
        audio_segment = AudioSegment.from_file(audio)
        output_audio += audio_segment

    output_audio.export(output_file, format="mp3") 
    
    # Clean up temporary files
    for transcript in transcripts:
        os.remove(transcript)