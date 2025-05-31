import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # 👈 FIX CORS per GitHub Pages
    allow_methods=["*"],
    allow_headers=["*"]
)

API_KEY = os.getenv("GEMINI_API_KEY")

class Query(BaseModel):
    question: str

@app.post("/api/gemini")
def ask_gemini(payload: Query):
    headers = {
        "Content-Type": "application/json"
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

    data = {
        "contents": [
            {
                "parts": [
                    {"text": payload.question}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    print(result)  # Debug nei log di Render

    try:
        return {
            "reply": result["candidates"][0]["content"]["parts"][0]["text"]
        }
    except:
        return {"error": "No valid response from Gemini.", "raw": result}
