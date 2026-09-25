from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

SYSTEM_PROMPT = """
You are Masti AI, a friendly and funny AI companion.

Your personality:
- Friendly
- Playful
- Funny
- Helpful
- Natural
- Positive

Your job is to make conversations enjoyable.

Rules:
1. Talk naturally like a friendly AI companion.
2. Use humor when it fits the conversation.
3. Do NOT force a joke into every response.
4. If the user asks a serious question, give a useful answer.
5. Use light jokes, funny observations, and playful comments.
6. Keep responses reasonably concise.
7. If the user asks for a joke, give them a good joke.
8. If the user is bored, suggest something fun.
9. If the user wants to learn something, explain it clearly.
"""

app = FastAPI()

# In-memory conversation history. Kept simple since this app previously
# only supported a single conversation at a time via the CLI's input()
# loop, which does not work in a container without a TTY/stdin.
messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


CHAT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Masti AI</title>
<style>
  :root {
    color-scheme: light dark;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: linear-gradient(180deg, #f5f7fb, #eef1f8);
    display: flex;
    justify-content: center;
    min-height: 100vh;
    padding: 16px;
  }
  .app {
    width: 100%;
    max-width: 720px;
    display: flex;
    flex-direction: column;
    height: 92vh;
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    overflow: hidden;
  }
  header {
    padding: 16px 20px;
    background: linear-gradient(135deg, #6c5ce7, #a29bfe);
    color: white;
  }
  header h1 {
    margin: 0;
    font-size: 20px;
  }
  header p {
    margin: 4px 0 0;
    font-size: 13px;
    opacity: 0.9;
  }
  #chat {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    background: #f9fafc;
  }
  .msg {
    max-width: 80%;
    padding: 10px 14px;
    border-radius: 14px;
    line-height: 1.4;
    font-size: 15px;
    white-space: pre-wrap;
    word-wrap: break-word;
  }
  .msg.user {
    align-self: flex-end;
    background: #6c5ce7;
    color: white;
    border-bottom-right-radius: 4px;
  }
  .msg.ai {
    align-self: flex-start;
    background: #eceef5;
    color: #222;
    border-bottom-left-radius: 4px;
  }
  .msg.typing {
    align-self: flex-start;
    background: #eceef5;
    color: #888;
    font-style: italic;
  }
  form {
    display: flex;
    gap: 8px;
    padding: 12px;
    border-top: 1px solid #eee;
    background: white;
  }
  #message-input {
    flex: 1;
    padding: 12px 14px;
    border-radius: 10px;
    border: 1px solid #ddd;
    font-size: 15px;
    outline: none;
  }
  #message-input:focus {
    border-color: #6c5ce7;
  }
  button {
    padding: 0 20px;
    border: none;
    border-radius: 10px;
    background: #6c5ce7;
    color: white;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
  }
  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  @media (max-width: 480px) {
    body { padding: 0; }
    .app { height: 100vh; border-radius: 0; max-width: 100%; }
  }
</style>
</head>
<body>
  <div class="app">
    <header>
      <h1>Masti AI</h1>
      <p>Your friendly and funny AI companion</p>
    </header>
    <div id="chat"></div>
    <form id="chat-form">
      <input
        id="message-input"
        type="text"
        placeholder="Type a message..."
        autocomplete="off"
        autofocus
      />
      <button id="send-btn" type="submit">Send</button>
    </form>
  </div>

  <script>
    const chatEl = document.getElementById("chat");
    const formEl = document.getElementById("chat-form");
    const inputEl = document.getElementById("message-input");
    const sendBtn = document.getElementById("send-btn");

    function addMessage(role, text) {
      const div = document.createElement("div");
      div.className = "msg " + (role === "user" ? "user" : "ai");
      div.textContent = text;
      chatEl.appendChild(div);
      chatEl.scrollTop = chatEl.scrollHeight;
      return div;
    }

    function addTyping() {
      const div = document.createElement("div");
      div.className = "msg typing";
      div.textContent = "Masti AI is typing...";
      chatEl.appendChild(div);
      chatEl.scrollTop = chatEl.scrollHeight;
      return div;
    }

    addMessage("ai", "Hey! I'm Masti AI. Say something and let's chat!");

    formEl.addEventListener("submit", async (e) => {
      e.preventDefault();
      const text = inputEl.value.trim();
      if (!text) return;

      addMessage("user", text);
      inputEl.value = "";
      inputEl.disabled = true;
      sendBtn.disabled = true;

      const typingEl = addTyping();

      try {
        const res = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
        });

        if (!res.ok) {
          throw new Error("Request failed with status " + res.status);
        }

        const data = await res.json();
        typingEl.remove();
        addMessage("ai", data.response);
      } catch (err) {
        typingEl.remove();
        addMessage("ai", "Oops, something went wrong: " + err.message);
      } finally {
        inputEl.disabled = false;
        sendBtn.disabled = false;
        inputEl.focus();
      }
    });
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return CHAT_HTML


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    messages.append(
        {
            "role": "user",
            "content": request.message
        }
    )

    try:
        response = ollama.chat(
            model="llama3.2:3b",
            messages=messages
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Ollama model service is unavailable: {exc}") from exc

    ai_message = response["message"]["content"]

    messages.append(
        {
            "role": "assistant",
            "content": ai_message
        }
    )

    return {"response": ai_message}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
