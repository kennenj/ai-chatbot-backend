from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# ✅ Enable CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 In-memory storage
user_memory = {}

# 📦 Request model
class ChatRequest(BaseModel):
    user_id: str
    message: str

# ✅ Root endpoint (fixes "Not Found")
@app.get("/")
def home():
    return {"status": "Backend running 🚀"}

# 🤖 Mock chatbot logic
def get_mock_response(user_id, message):
    msg = message.lower()

    # Store name
    if "my name is" in msg:
        name = msg.split("is")[-1].strip()
        user_memory[user_id] = {"name": name}
        return f"Nice to meet you, {name}! 😊"

    # Recall name
    if "what is my name" in msg:
        name = user_memory.get(user_id, {}).get("name", "I don't know yet 😅")
        return f"Your name is {name}"

    # Greetings
    if "hi" in msg or "hello" in msg:
        return "Hi yaar! Kaise ho? 😊"

    if "how are you" in msg:
        return "Main mast hoon 😄 tum batao?"

    return "Tell me more 😊"

# 🚀 Chat endpoint
@app.post("/chat")
def chat(req: ChatRequest):
    user_id = req.user_id
    message = req.message

    try:
        reply = get_mock_response(user_id, message)
        return {"reply": reply}

    except Exception as e:
        return {"error": str(e)}
