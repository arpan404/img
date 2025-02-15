from google import genai
import os



def get_content(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    print(api_key)
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.0-flash-001', contents=prompt
    )
    return response.text
