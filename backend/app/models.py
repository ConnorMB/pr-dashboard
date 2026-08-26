from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pull_requests: Mapped[list["PullRequest"]] = relationship(back_populates="repository")

    __table_args__ = (UniqueConstraint("owner", "name", name="uq_repository_owner_name"),)


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repo_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    merged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)
    changed_files: Mapped[int] = mapped_column(Integer, default=0)
    repository: Mapped["Repository"] = relationship(back_populates="pull_requests")
    reviews: Mapped[list["Review"]] = relationship(back_populates="pull_request")

    __table_args__ = (UniqueConstraint("repo_id", "number", name="uq_pull_request_repo_number"),)


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pull_request_id: Mapped[int] = mapped_column(ForeignKey("pull_requests.id"), nullable=False)
    reviewer: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    pull_request: Mapped["PullRequest"] = relationship(back_populates="reviews")