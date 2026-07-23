from fastapi import FastAPI

app = FastAPI(title="PR Analytics Dashboard")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
