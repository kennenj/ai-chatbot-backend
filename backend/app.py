from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# ✅ CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ API KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 🔥 USE AI
USE_AI = True

# In-memory storage (optional, for future use)
user_memory = {}

class ChatRequest(BaseModel):
    user_id: str
    message: str

# -------------------------
# 🟢 MOCK (fallback if AI disabled)
# -------------------------
def get_mock_response(user_id, message):
    return "AI not enabled yet"

# -------------------------
# 🔵 GEMINI CALL FUNCTION
# -------------------------
def call_gemini(model, message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [{"text": message}]
            }
        ]
    }

    response = requests.post(url, json=payload)
    return response.json()

# -------------------------
# 🔵 GEMINI RESPONSE (RETRY + FALLBACK)
# -------------------------
def get_gemini_response(message):
    models = [
        "gemini-flash-latest",   # Primary (best + auto-updated)
        "gemini-2.0-flash"      # Fallback (very stable)
    ]

    for model in models:
        for attempt in range(2):  # Retry twice per model
            try:
                result = call_gemini(model, message)

                # ✅ Success case
                if "candidates" in result:
                    return result["candidates"][0]["content"]["parts"][0]["text"]

                # ❌ If API error (like 503), try next attempt/model
                if "error" in result:
                    continue

            except Exception:
                continue

    # ❌ Final fallback (user-friendly message)
    return "Sorry, AI is busy right now. Please try again in a moment."

# -------------------------
# 🚀 ROOT ENDPOINT
# -------------------------
@app.get("/")
def home():
    return {"status": "Backend running 🚀"}

# -------------------------
# 🚀 CHAT ENDPOINT
# -------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        if USE_AI:
            reply = get_gemini_response(req.message)
        else:
            reply = get_mock_response(req.user_id, req.message)

        return {"reply": reply}

    except Exception as e:
        return {"reply": f"Error: {str(e)}"}