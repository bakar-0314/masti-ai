import os
from pathlib import Path

from openai import OpenAI
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import (
    init_database,
    create_conversation,
    add_message,
    get_messages,
    get_conversations,
    get_conversation,
)



BASE_DIR = Path(__file__).resolve().parent
FRONTEND_FILE = BASE_DIR / "static" / "index.html"

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)




app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_hf_client():
    token = os.getenv("HF_TOKEN") or os.getenv("HF_API_KEY")

    if not token:
        raise HTTPException(
            status_code=500,
            detail="HF_TOKEN or HF_API_KEY is not set. Add it to your deployment environment.",
        )

    return OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=token,
    )


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


init_database()


@app.get("/")
@app.get("/debug-files")
def debug_files():
    static_dir = BASE_DIR / "static"

    return {
        "base_dir": str(BASE_DIR),
        "static_exists": static_dir.exists(),
        "static_files": [
            str(p.relative_to(BASE_DIR))
            for p in static_dir.rglob("*")
        ] if static_dir.exists() else []
    }
def home():
    if not FRONTEND_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="Frontend file not found: static/index.html",
        )

    return FileResponse(FRONTEND_FILE)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "masti-ai",
    }


@app.post("/new-chat", response_model=NewChatResponse)
def new_chat():
    conversation_id = create_conversation()
    return {"conversation_id": conversation_id}


@app.post("/chat")
def chat(request: ChatRequest):
    add_message(
        request.conversation_id,
        "user",
        request.message,
    )

    history = get_messages(request.conversation_id)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]
    messages.extend(history)

    print(
        f"CHAT: conversation={request.conversation_id}, "
        f"message={request.message}"
    )

    try:
        print("HF: Connecting to Hugging Face...", flush=True)
        client = get_hf_client()

        print("HF: Sending request...", flush=True)
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
        )

        ai_message = response.choices[0].message.content
        print("HF: Response received", flush=True)

    except Exception as e:
        print(f"HF ERROR TYPE: {type(e).__name__}", flush=True)
        print(f"HF ERROR DETAILS: {str(e)}", flush=True)

        raise HTTPException(
            status_code=502,
            detail=f"{type(e).__name__}: {str(e)}",
        ) from e

    if not ai_message:
        raise HTTPException(
            status_code=502,
            detail="The AI returned an empty response.",
        )

    add_message(
        request.conversation_id,
        "assistant",
        ai_message,
    )

    print("CHAT: response generated")

    return {"response": ai_message}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
    )