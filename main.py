import os
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Sostituisci con la tua chiave o caricala da environment
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

    try:
        return {
            "reply": result["candidates"][0]["content"]["parts"][0]["text"]
        }
    except:
        return {"error": "No valid response from Gemini."}
