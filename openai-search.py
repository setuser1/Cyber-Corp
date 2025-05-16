import os
from openai import OpenAI

LMSTUDIO_API_KEY = "lm-studio"
LMSTUDIO_API_BASE = "https://localhost:80/v1"

# ─── Initialize client ─────────────────────────────────────────────────────────

client = OpenAI(
    api_key=LMSTUDIO_API_KEY,
    api_base=LMSTUDIO_API_BASE,
)

# ─── Build messages with a system prompt ───────────────────────────────────────

messages = [
    {
        "role": "system",
        "content": "You are an AI tool that only reports technology articles from techcrunch and wired."
    },
    {
        "role": "user",
        "content": "What was a tech story from today?"
    }
]

# ─── Send request to LM Studio ────────────────────────────────────────────────

response = client.chat.completions.create(
    model="gemma-27b",
    tools=[{"type": "web_search_preview"}],
    messages=messages
)

# ─── Capture & print the output ───────────────────────────────────────────────

ai_response = response.choices[0].message.content
print(ai_response)
