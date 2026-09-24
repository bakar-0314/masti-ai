import os

import ollama
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

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


@app.get("/")
def health():
    return {"status": "ok", "service": "masti-ai"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    messages.append(
        {
            "role": "user",
            "content": request.message
        }
    )

    response = ollama.chat(
        model="llama3.2:3b",
        messages=messages
    )

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
