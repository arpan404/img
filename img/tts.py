"""
This module provides a function to convert text to speech using the Dia model.
It includes functionality to chunk transcripts based on word count and speaker consistency,
and to remove silence from the generated audio.
It uses the pydub library for audio manipulation and librosa for silence removal.
"""

import os
import re
import tempfile
from typing import List

import librosa
import numpy as np
import soundfile as sf
from dia.model import Dia
from pydub import AudioSegment


# Chunk transcript based on word count and speaker consistency
def chunk_transcripts(text: str, min_words: int = 20, max_words: int = 50) -> List[str]:
    chunks = []
    buffer = ""
    buffer_word_count = 0
    current_speaker = None

    for line in text.splitlines():
        line = line.strip()
        if not line or not line.startswith("[S"):
            continue

        match = re.match(r"\[(S\d)\](.*)", line)
        if not match:
            continue

        speaker, dialogue = match.groups()
        dialogue = dialogue.strip()
        full_line = f"[{speaker}] {dialogue}"
        word_count = len(dialogue.split())

        if current_speaker == speaker or not buffer:
            buffer += " " + full_line
            buffer_word_count += word_count
            current_speaker = speaker
            if buffer_word_count >= max_words:
                chunks.append(buffer.strip())
                buffer = ""
                buffer_word_count = 0
        else:
            if buffer_word_count >= min_words:
                chunks.append(buffer.strip())
                buffer = f"{full_line}"
                buffer_word_count = word_count
                current_speaker = speaker
            else:
                buffer += " " + full_line
                buffer_word_count += word_count

    if buffer and buffer_word_count >= min_words:
        chunks.append(buffer.strip())

    return chunks


def text_to_speech(text: str, output_file: str) -> None:
    # Get the directory of the current script
    script_dir = os.path.abspath(os.path.dirname(__file__))

    # Go up one level to the parent 'img' directory
    parent_dir = os.path.abspath(os.path.join(script_dir, ".."))

    # Build audio paths from the parent directory
    audio_dir = os.path.join(parent_dir, "audio")
    print("Loading Dia model...")
    model = Dia.from_pretrained("nari-labs/Dia-1.6B", compute_dtype="float16")
    print("Model loaded!")

    # Chunk the text
    print("✂️ Chunking transcript...")
    transcript_chunks = chunk_transcripts(text, min_words=30)
    if not transcript_chunks:
        raise ValueError("No valid dialogue lines found.")

    # Create temp folder to hold audio clips
    audio_temp_dir = tempfile.mkdtemp()
    audio_files = []

    print("Generating audio for each chunk...")
    for i, transcript in enumerate(transcript_chunks):
        speaker_match = re.match(r"\[(S\d)\]", transcript)
        speaker = speaker_match.group(1) if speaker_match else "S1"
        clean_transcript = transcript.replace("[PAUSE]", "").strip()

        print(f"({speaker}) Chunk {i + 1}: {clean_transcript}")

        if speaker == "S2":
            speaker_prompt_audio = os.path.join(audio_dir, "audio_prompt.mp3")
            clone_from_text = "[S2] Hello everyone! This is the second voice. Hope you all love it. [S1] Hello Everyone! Welcome to the room of chaos. Nobody knows how the code works.[S2]"
        else:
            speaker_prompt_audio = os.path.join(audio_dir, "prompt_audio.mp3")

            clone_from_text = "[S1] Hello Everyone! Welcome to the room of chaos. Nobody knows how the code works. [S2] Hello everyone! This is the second voice. Hope you all love it.[S1]"

        if not os.path.exists(speaker_prompt_audio):
            raise FileNotFoundError(
                f"Prompt audio for {speaker} not found: {speaker_prompt_audio}"
            )

        # Generate audio
        audio = model.generate(
            clone_from_text + clean_transcript.strip() + ". [PAUSE]",
            audio_prompt=speaker_prompt_audio,
            use_torch_compile=False,
            verbose=False,
        )

        output_path = os.path.join(audio_temp_dir, f"{speaker}_{i}.mp3")
        model.save_audio(output_path, audio)
        audio_files.append(output_path)

    # Combine all audio clips
    print("Concatenating audio chunks...")
    final_audio = AudioSegment.empty()
    for audio_path in audio_files:
        segment = AudioSegment.from_file(audio_path)
        final_audio += segment

    final_audio.export(output_file, format="mp3")
    print(f"Final audio saved to: {output_file}")

    # Clean up temporary files
    for path in audio_files:
        os.remove(path)
    os.rmdir(audio_temp_dir)


# If needed: Remove silence
def remove_silence(input_file: str, output_file: str, silence_threshold=-50.0):
    print("Removing silence...")
    audio, sr = librosa.load(input_file)
    non_silent_intervals = librosa.effects.split(audio, top_db=40)

    if len(non_silent_intervals) == 0:
        print(" No non-silent parts found. Check the input or adjust top_db.")
        return

    # Extract non-silent parts
    cleaned_audio = np.concatenate(
        [audio[start:end] for start, end in non_silent_intervals]
    )
    output_cleaned = os.path.splitext(output_file)[0] + "_cleaned.mp3"

    sf.write(output_cleaned, cleaned_audio, sr)
    print(f"Cleaned audio saved to: {output_cleaned}")
