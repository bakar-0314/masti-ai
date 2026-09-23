from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import ollama

from database import (
    init_database,
    create_conversation,
    add_message,
    get_messages
)

app = FastAPI()


SYSTEM_PROMPT = """
You are Masti AI, a friendly and funny AI companion.

Your personality:
- Friendly
- Playful
- Funny
- Helpful
- Natural
- Positive

Your goal is to make conversations enjoyable.

Rules:
1. Talk naturally like a friendly AI companion.
2. Use humor when it fits the conversation.
3. Do not force a joke into every response.
4. If the user asks a serious question, give a useful answer.
5. Use light jokes, funny observations, and playful comments.
6. Keep responses reasonably concise.
7. If the user asks for a joke, give them a good joke.
8. If the user is bored, suggest something fun.
9. If the user wants to learn something, explain it clearly.
10. Remember information from the current conversation.
"""


class ChatRequest(BaseModel):
    conversation_id: int
    message: str


class NewChatResponse(BaseModel):
    conversation_id: int


# Create database when server starts
init_database()


@app.post("/new-chat", response_model=NewChatResponse)
def new_chat():
    conversation_id = create_conversation()

    return {
        "conversation_id": conversation_id
    }


@app.post("/chat")
def chat(request: ChatRequest):

    # Save user message
    add_message(
        request.conversation_id,
        "user",
        request.message
    )

    # Load conversation history
    history = get_messages(request.conversation_id)

    # Add system instructions
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(history)

    # Ask Ollama
    response = ollama.chat(
        model="llama3.2:3b",
        messages=messages
    )

    ai_message = response["message"]["content"]

    # Save AI response
    add_message(
        request.conversation_id,
        "assistant",
        ai_message
    )

    return {
        "response": ai_message
    }


@app.get("/")
def home():
    return FileResponse("static/index.html")