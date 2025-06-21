import google.generativeai as genai
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# Create FastAPI app
app = FastAPI()

# Setup CORS if frontend runs on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Backend running!"}

# Actual endpoint you want
@app.post("/generate_narration")
async def generate_narration(poi: str):
    response = model.generate_content(
        f"Give me a short friendly tour guide narration for: {poi}"
    )
    return {"narration": response.text}