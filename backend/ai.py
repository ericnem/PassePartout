import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-pro')

def generate_narration(poi):
    response = model.generate_content(
        f"Give me a short friendly tour guide narration for: {poi}"
    )
    return response.text