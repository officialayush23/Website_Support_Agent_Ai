# app/main.py

from fastapi import FastAPI

app = FastAPI(
    title="Website Support Agent AI",
    version="1.0.0",
)

@app.get("/health")
async def health():
    return {"status": "ok"}
