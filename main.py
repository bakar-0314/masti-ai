import ollama

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

messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

print("😂 Masti AI is ready!")
print("Type 'exit' to stop the conversation.\n")

while True:

    user_message = input("You: ")

    if user_message.lower() == "exit":
        print("\n😂 Masti AI: Bye! Come back when boredom attacks again! 😎")
        break

    messages.append(
        {
            "role": "user",
            "content": user_message
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

    print("\n😂 Masti AI:")
    print(ai_message)
    print()