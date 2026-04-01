from mem0 import Memory
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Mem0 Config ───────────────────────────────────────────────────────────────
config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": os.getenv("GEMINI_API_KEY"),
            "model": "text-embedding-004",
            "openai_base_url": "https://generativelanguage.googleapis.com/v1beta/openai/"
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": os.getenv("GEMINI_API_KEY"),
            "model": "gemini-1.5-flash-latest",
            "openai_base_url": "https://generativelanguage.googleapis.com/v1beta/openai/"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "my_collection"
        }
    }
}

mem_client = Memory.from_config(config)

# ─── OpenAI-compatible Gemini Client ───────────────────────────────────────────
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

USER_ID = "urvil"

# ─── Chat Loop ─────────────────────────────────────────────────────────────────
print("Chat started! Type 'exit' to quit.\n")

while True:
    user_query = input("You: ").strip()

    if user_query.lower() == "exit":
        print("Goodbye!")
        break

    # Retrieve relevant memories
    memories = mem_client.search(query=user_query, user_id=USER_ID)
    memory_context = "\n".join(
        f"- {m['memory']}" for m in memories.get("results", [])
    )

    system_prompt = "You are a helpful assistant with memory of past conversations."
    if memory_context:
        system_prompt += f"\n\nRelevant memory about the user:\n{memory_context}"

    # Call Gemini
    response = client.chat.completions.create(
        model="gemini-1.5-flash-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_query}
        ]
    )

    ai_response = response.choices[0].message.content
    print(f"AI: {ai_response}\n")

    # Save to memory
    mem_client.add(
        messages=[
            {"role": "user",      "content": user_query},
            {"role": "assistant", "content": ai_response}
        ],
        user_id=USER_ID
    )