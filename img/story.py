"""
    This module contains the code for generating the story, both text and audio.
    It uses openai's SDK to generate the story and Dia-1.6B to generate the audio.
"""
from os import getenv

from openai import OpenAI

SYSTEM_PROMPT = """
You are a story generator. You will be given a prompt and you will generate a story based on that prompt.
"""

LLM_API_KEY = getenv("LLM_API_KEY")
LLM_API_URL = getenv("LLM_API_URL")
LLM_MODEL_NAME = getenv("LLM_MODEL_NAME")
LLM_TEMPERATURE = float(getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(getenv("LLM_MAX_TOKENS", "10000"))

assert LLM_API_KEY, "LLM_API_KEY not set. Please set it in your environment variables."
assert LLM_API_URL, "LLM_API_URL not set. Please set it in your environment variables."
assert LLM_MODEL_NAME, "LLM_MODEL_NAME not set. Please set it in your environment variables."

def generate_story(prompt: str) -> str:
    """
    Generate a story based on the prompt provided.

    :param prompt: The prompt to generate the story from.
    :return: The generated story.
    """
    client = OpenAI(
        api_key=LLM_API_KEY,
        base_url=LLM_API_URL
    )
    response = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS
    )
    # if response.status_code != 200:
    #     raise Exception(f"Error generating story: {response.text}")
    story = response.choices[0].message.content
    return story