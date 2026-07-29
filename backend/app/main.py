import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db import SessionLocal, init_db
from app.ingest import sync_repository
from app.metrics import (
    pr_size_distribution,
    review_turnaround_hours,
    time_to_merge_hours,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="PR Analytics Dashboard", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://pr-dashboard-1.onrender.com",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest")
def ingest(session: Session = Depends(get_session)) -> dict:
    owner, repo = os.environ["GITHUB_REPO"].split("/")
    token = os.environ.get("GITHUB_TOKEN") or None
    return sync_repository(session, owner, repo, token)


@app.get("/metrics/time-to-merge")
def get_time_to_merge(session: Session = Depends(get_session)) -> list[dict]:
    return time_to_merge_hours(session)


@app.get("/metrics/review-turnaround")
def get_review_turnaround(session: Session = Depends(get_session)) -> list[dict]:
    return review_turnaround_hours(session)


@app.get("/metrics/pr-size")
def get_pr_size(session: Session = Depends(get_session)) -> list[dict]:
    return pr_size_distribution(session)
