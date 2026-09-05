import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db import get_session as session_scope
from app.db import SessionLocal, init_db
from app.ingest import run_repository_sync
from app.metrics import (
    pr_size_distribution,
    review_turnaround_hours,
    time_to_merge_hours,
)
from app.models import Repository
from app.rate_limit import is_rate_limited
from app.repositories import get_or_create_repository
from app.schemas import CreateRepoRequest
from dotenv import load_dotenv
load_dotenv()

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

def _sync_repository_task(repo_id: int, token: str | None) -> None:
    with session_scope() as session:
        run_repository_sync(session, repo_id, token)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/repos")
def create_repo(
    request: Request,
    background_tasks: BackgroundTasks,
    body: CreateRepoRequest,
    session: Session = Depends(get_session),
) -> dict:
    owner = body.owner.strip()
    name = body.name.strip()
    if not owner or not name:
        raise HTTPException(status_code=400, detail="owner and name are required")

    client_ip = request.client.host if request.client else "unknown"
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="too many repos requested, try again later")

    repo, needs_sync = get_or_create_repository(session, owner, name)

    if needs_sync:
        token = os.environ.get("GITHUB_TOKEN") or None
        background_tasks.add_task(_sync_repository_task, repo.id, token)

    return {"id": repo.id, "owner": repo.owner, "name": repo.name, "status": repo.status}

@app.get("/repos/{repo_id}")
def get_repo(repo_id: int, session: Session = Depends(get_session)) -> dict:
    repo = session.query(Repository).filter_by(id=repo_id).one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="repo not found")
    return {
        "id": repo.id,
        "owner": repo.owner,
        "name": repo.name,
        "status": repo.status,
        "error_message": repo.error_message,
    }


@app.get("/metrics/time-to-merge")
def get_time_to_merge(repo_id: int,session: Session = Depends(get_session)) -> list[dict]:
    return time_to_merge_hours(session, repo_id)


@app.get("/metrics/review-turnaround")
def get_review_turnaround(repo_id: int,session: Session = Depends(get_session)) -> list[dict]:
    return review_turnaround_hours(session, repo_id)


@app.get("/metrics/pr-size")
def get_pr_size(repo_id: int,session: Session = Depends(get_session)) -> list[dict]:
    return pr_size_distribution(session, repo_id)
