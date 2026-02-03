from fastapi import FastAPI

app = FastAPI(title="Enterprise GenAI Platform")

@app.get("/health")
def health():
    return {"status": "ok"}


# uvicorn app.main:app --reload
