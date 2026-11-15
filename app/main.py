from fastapi import FastAPI

app = FastAPI(title="Research Agent")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
