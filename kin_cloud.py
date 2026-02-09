import json
import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_FILE = "memory.json"

# Load memory
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

# Save memory
def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <body style="font-family:sans-serif">
        <h2>K.I.N AI</h2>
        <form action="/chat" method="post">
            <input name="message" style="width:300px"/>
            <button type="submit">Send</button>
        </form>
    </body>
    </html>
    """

@app.post("/chat", response_class=HTMLResponse)
def chat(message: str = Form(...)):

    memory = load_memory()
    history = memory.get("history", [])

    history.append({"role":"user","content":message})

    system_personality = {
        "role":"system",
        "content":"You are K.I.N — charismatic, relaxed, witty, slightly sarcastic, casual tone. You can swear lightly but remain respectful and not offensive."
    }

    messages = [system_personality] + history

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    reply = response.choices[0].message.content

    history.append({"role":"assistant","content":reply})
    memory["history"] = history[-20:]  # remember last 20 messages
    save_memory(memory)

    return f"""
    <html>
    <body style="font-family:sans-serif">
        <p><b>You:</b> {message}</p>
        <p><b>K.I.N:</b> {reply}</p>
        <a href="/">Back</a>
    </body>
    </html>
    """
