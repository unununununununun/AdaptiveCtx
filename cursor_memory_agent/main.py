"""Cursor agent that uses AdaptiveCtx memory service.

How it works (tested with Cursor 1.33):
• Cursor sends each user message as one JSON line on STDIN:
    {"role": "user", "content": "Hello"}
• We read that line, extract text, call memory_service /query to get
  relevant past Q/A pairs, build a simple prompt (demo: echo + context),
  print assistant reply to STDOUT (plain text) — Cursor shows it.
• We immediately call /update to save the new pair so that the next
  turn already has updated memory.

To use:
1. Ensure AdaptiveCtx API is running on localhost:8000 (docker compose up -d).
2. In Cursor add an agent:
   Directory → cursor_memory_agent
   Entry     → main.py
3. Run.  Type in chat, replies appear and memory grows.
"""
import sys, json, os

from memory_client import query, update

NS   = os.getenv("MEMORY_NS", "chat")
TOPK = int(os.getenv("MEMORY_TOPK", "4"))

print("AdaptiveCtx memory agent ready", file=sys.stderr, flush=True)

def read_user() -> str:
    """Read one user message from STDIN (Cursor JSON line)."""
    line = sys.stdin.readline()
    if not line:
        return ""
    line = line.strip()
    try:
        obj = json.loads(line)
        if isinstance(obj, dict) and obj.get("role") == "user":
            return obj.get("content", "")
    except json.JSONDecodeError:
        pass
    return line  # fallback: raw text

def main() -> None:
    while True:
        user_text = read_user()
        if not user_text:
            continue
        if user_text.lower() == "exit":
            break

        # 1) fetch context from memory
        slots = query(user_text, ns=NS, k=TOPK)
        ctx_block = "\n".join(s["text"] for s in slots)
        if ctx_block:
            print("[ctx]\n" + ctx_block, file=sys.stderr, flush=True)

        # 2) generate assistant reply (demo: echo)
        assistant = f"[Echo] {user_text}"

        # 3) output reply to Cursor (plain text)
        print(assistant, flush=True)

        # 4) store new pair in memory
        update(user_text, assistant, ns=NS)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass