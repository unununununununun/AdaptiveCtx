"""Minimal Cursor agent example that uses AdaptiveCtx memory.

How to run (locally):
1. Start AdaptiveCtx service on localhost:8000 (docker compose up -d).
2. Set env vars (optional, already default):
      MEMORY_API=http://localhost:8000
      MEMORY_API_KEY=secret123
3. Run this script:
      python main.py
"""
import os
from cursor_client import query, update

def main():
    print("AdaptiveCtx demo. Type 'exit' to quit.")
    ns = os.getenv("MEMORY_NS", "chat")
    while True:
        user = input("You: ").strip()
        if user.lower() == "exit":
            break
        # fetch context
        slots = query(user, ns=ns, k=4)
        ctx = "\n".join(s["text"] for s in slots)
        print("--- retrieved context ---------------------")
        print(ctx or "<empty>")
        # dummy assistant reply (echo)
        assistant = f"[Echo] {user}"
        print("Assistant:", assistant)
        # store pair
        update(user, assistant, ns=ns)

if __name__ == "__main__":
    main()