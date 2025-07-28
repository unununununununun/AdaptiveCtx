"""Cursor integration package for AdaptiveCtx

Provides thin HTTP helper to interact with running AdaptiveCtx memory service.
Place `cursor_client` folder inside your agent's project and use:

    from cursor_client import query, update
    slots = query("user message")

Configure via env vars:
    MEMORY_API      (default http://localhost:8000)
    MEMORY_API_KEY  (default secret123)
"""

from .client import query, update  # re-export