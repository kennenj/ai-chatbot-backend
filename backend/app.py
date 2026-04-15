from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# ✅ Enable CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ API KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 🔥 Toggle AI
USE_AI = True

# Optional: memory storage
user_memory = {}

# Request model
class ChatRequest(BaseModel):
    user_id: str
    message: str


# -------------------------
# 🟢 MOCK (fallback)
# -------------------------
def get_mock_response(user_id, message):
    return "AI not enabled yet"


# -------------------------
# 🔵 GEMINI RESPONSE
# -------------------------
def get_gemini_response(message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": message}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        return result["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"Gemini Error: {str(e)} | Full Response: {result}"


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


# -------------------------
# ▶️ RUN SERVER (FOR RENDER)
# -------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 10000))

    uvicorn.run(app, host="0.0.0.0", port=port)