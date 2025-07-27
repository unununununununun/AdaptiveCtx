from fastapi import FastAPI\n\napp = FastAPI(title="adaptive-memory (stub)")\n\n@app.get("/health")\nasync def health():\n    return {"status": "ok"}\n
