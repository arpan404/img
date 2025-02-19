import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf

def generate_audio(path:str, text:str= "hello", description:str="ho"):
    device = "cuda:0" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

    print("device: ", device)


    model = ParlerTTSForConditionalGeneration.from_pretrained("parler-tts/parler-tts-mini-v1.1").to(device)
    tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-v1.1")
    description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)

    prompt = """Okay, so you won't BELIEVE what I heard about Olivia and Mark. You know, Olivia, the CEO's wife? And Mark, her personal trainer? Well, apparently, everyone at the country club has been buzzing about their "intense" workout sessions for months, right? But it was all just whispers, you know, nothing concrete."""
    description = "A female speaker delivers a slightly expressive and animated speech with a moderate speed and pitch. The recording is of very high quality, with the speaker's voice sounding clear and very close up."

    input_ids = description_tokenizer(description, return_tensors="pt").input_ids.to(device)
    prompt_input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

    generation = model.generate(input_ids=input_ids, prompt_input_ids=prompt_input_ids)
    audio_arr = generation.cpu().numpy().squeeze()
    sf.write(path, audio_arr, model.config.sampling_rate)