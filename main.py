from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests

app = FastAPI()

# CORS middleware CORRETTO e COMPLETO
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sawyerbatch.github.io"], #allow_origins=["*"],  # o specifica il tuo dominio GitHub Pages
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

API_KEY = os.getenv("GEMINI_API_KEY")
print("USING API KEY:", API_KEY)
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

    print("GEMINI RAW RESPONSE:", result)

    try:
        return {
            "reply": result["candidates"][0]["content"]["parts"][0]["text"]
        }
    except Exception as e:
        return {"error": str(e), "raw": result}


@app.get("/")
def ping():
    return {"message": "ok"}