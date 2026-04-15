from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = FastAPI()

# -------------------------
# CORS (for frontend UI)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# CONFIG
# -------------------------
USE_AI = True

# Memory storage
chat_history = {}
user_memory = {}

# -------------------------
# REQUEST MODEL
# -------------------------
class ChatRequest(BaseModel):
    user_id: str
    message: str

# -------------------------
# MEMORY: extract name
# -------------------------
def extract_memory(user_id, message):
    msg = message.lower()

    if "my name is" in msg:
        name = message.split("is")[-1].strip()
        user_memory[user_id] = {"name": name}

# -------------------------
# GET MEMORY TEXT
# -------------------------
def get_memory_text(user_id):
    memory = user_memory.get(user_id, {})
    text = ""

    if "name" in memory:
        text += f"User name is {memory['name']}.\n"

    return text

# -------------------------
# MOCK BOT (fallback)
# -------------------------
def get_mock_response(message):
    msg = message.lower()

    if "hi" in msg or "hello" in msg:
        return "Hey! Kaise ho? 😊"

    if "how are you" in msg:
        return "Main mast hoon 😄 tum batao?"

    return "Tell me more 😊"

# -------------------------
# GEMINI AI FUNCTION
# -------------------------
def get_ai_response(user_id, message):
    history = chat_history.get(user_id, [])

    system_prompt = """
You are a friendly Indian AI companion.
Talk like a real human friend.
Use Hinglish naturally.
Be conversational, short, and engaging.
Ask follow-up questions.
"""

    contents = [
        {"parts": [{"text": system_prompt}]}
    ]

    # add memory
    memory_text = get_memory_text(user_id)
    if memory_text:
        contents.append({"parts": [{"text": memory_text}]})

    # add chat history
    for msg in history:
        contents.append({"parts": [{"text": msg}]})

    # current message
    contents.append({"parts": [{"text": message}]})

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={os.getenv('GEMINI_API_KEY')}"

        payload = {"contents": contents}

        response = requests.post(url, json=payload)
        data = response.json()

        reply = data["candidates"][0]["content"]["parts"][0]["text"]

        # save history
        chat_history.setdefault(user_id, []).append(f"User: {message}")
        chat_history[user_id].append(f"AI: {reply}")

        return reply

    except Exception as e:
        print("Gemini Error:", e)
        return "Error aaya 😢 try again!"

# -------------------------
# MAIN CHAT ENDPOINT
# -------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    user_id = req.user_id
    message = req.message

    extract_memory(user_id, message)

    try:
        if USE_AI:
            reply = get_ai_response(user_id, message)
        else:
            reply = get_mock_response(message)

        return {"reply": reply}

    except Exception as e:
        return {"error": str(e)}

# -------------------------
# HEALTH CHECK
# -------------------------
@app.get("/")
def home():
    return {"status": "AI Chatbot running 🚀"}