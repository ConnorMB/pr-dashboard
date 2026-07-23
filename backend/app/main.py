from fastapi import FastAPI

from app.db import init_db

app = FastAPI(title="PR Analytics Dashboard")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
