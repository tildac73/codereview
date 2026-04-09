from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    error = "error"
    warning = "warning"
    suggestion = "suggestion"
    nitpick = "nitpick"


class Category(str, Enum):
    security = "security"
    performance = "performance"
    logic = "logic"
    style = "style"
    docs = "docs"


class Hunk(SQLModel):
    """
    Represents one changed block within a file.
    Produced by diff_parser.py, consumed by batcher.py.
    NOT stored in DB — it's a transient intermediate object.
    """
    file: str # e.g. "src/auth/login.py"
    language: str # e.g. "python" — detected from extension
    line_start: int
    line_end: int
    before: str # the removed lines (prefixed with -)
    after: str # the added lines (prefixed with +)
    context: str # surrounding unchanged lines for LLM context


class Batch(SQLModel):
    """
    A group of hunks sent to the LLM together.
    Produced by batcher.py.
    """
    hunks: list[Hunk]
    token_estimate: int # rough estimate before sending


class ReviewComment(SQLModel, table=True):
    """
    One piece of feedback from the LLM. Stored in the DB.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int # foreign key → Run.id
    file: str
    line_start: int
    line_end: int
    severity: Severity
    category: Category
    title: str # short label, e.g. "SQL injection risk"
    body: str # full explanation
    suggested_fix: Optional[str] = None
    prompt_version: str # e.g. "v1.1" — critical for evals


class Run(SQLModel, table=True):
    """
    One invocation of the review tool.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    git_ref: str # e.g. "HEAD~1" or PR URL
    prompt_version: str
    total_comments: int
    raw_diff_hash: str # sha256 of the diff — used for caching
