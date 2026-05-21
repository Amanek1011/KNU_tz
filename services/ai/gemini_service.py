from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_text(prompt):
    response = client.models.generate_content(
        model="gemini-1.5-pro",
        contents=prompt
    )
    return response.text


print(analyze_text("Скажи: API работает"))

