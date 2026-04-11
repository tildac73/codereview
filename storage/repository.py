from sqlmodel import select
from storage.database import get_session
from core.models import Run, ReviewComment

def save_run(run: Run, comments: list[ReviewComment]) -> int:
    with get_session() as session:
        session.add(run)
        session.commit()
        session.refresh(run)
        run_id = run.id

        for comment in comments:
            comment.run_id = run_id
            session.add(comment)
        session.commit()

    return run_id

def get_comments(run_id: int, severity=None, category=None) -> list[ReviewComment]:
    with get_session() as session:
        query = select(ReviewComment).where(ReviewComment.run_id == run_id)
        if severity: query = query.where(ReviewComment.severity == severity)
        if category: query = query.where(ReviewComment.category == category)
        return session.exec(query).all()
