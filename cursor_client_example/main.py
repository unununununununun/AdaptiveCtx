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
import json
from textwrap import dedent
from cursor_client import query, update

def main():
    # optional console prompt (visible only when run in a terminal)
    if os.isatty(0):  # stdin is tty
        print("AdaptiveCtx demo. Type 'exit' to quit.")

    ns = os.getenv("MEMORY_NS", "chat")

    # optional: OpenAI key to generate real answers
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_client = None
    if openai_key:
        try:
            import openai
            openai_client = openai.OpenAI(api_key=openai_key)
        except ModuleNotFoundError:
            print("[warning] openai package not installed – falling back to echo mode.")
            openai_client = None

    def llm_reply(prompt: str) -> str:
        """Call OpenAI chat completion or fallback echo."""
        if not openai_client:
            return f"[Echo] {prompt.strip()}"
        try:
            chat_resp = openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            return chat_resp.choices[0].message.content.strip()
        except Exception as e:
            print("[error] OpenAI call failed:", e)
            return f"[Echo-err] {prompt.strip()}"

    import sys

    def read_user_line() -> str:
        """Read from stdin; accept raw text or Cursor JSON payload."""
        raw = sys.stdin.readline()
        if not raw:
            return ""  # EOF
        raw = raw.strip()
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict) and obj.get("role") == "user":
                return obj.get("content", "").strip()
        except json.JSONDecodeError:
            pass
        return raw

    while True:
        user = read_user_line()
        if not user:
            continue
        if user.lower() == "exit":
            break

        # 1) retrieve context memory
        slots = query(user, ns=ns, k=4)
        context_block = "\n".join(s["text"] for s in slots)

        # 2) build prompt for LLM (few-shot with memory)
        prompt_parts = [
            "Below are previous relevant Q/A pairs (may be empty):",
            context_block or "<none>",
            "Current user question:",
            user,
        ]
        prompt = "\n\n".join(prompt_parts)

        # 3) generate assistant answer
        assistant = llm_reply(prompt)

        print("--- retrieved context ---------------------", flush=True)
        print(context_block or "<empty>", flush=True)
        print("Assistant:", assistant, flush=True)

        # 4) store new Q/A into memory
        update(user, assistant, ns=ns)

if __name__ == "__main__":
    main()