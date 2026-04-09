import anthropic
import pytest
from unittest.mock import patch, MagicMock
from core.models import Batch, Hunk, Severity, Category
from llm.client import analyze_batch, call_with_retry


def make_batch():
    hunk = Hunk(
        file="src/auth.py",
        language="python",
        line_start=10,
        line_end=12,
        before='query = f"SELECT * FROM users WHERE name = {user}"',
        after='query = "SELECT * FROM users WHERE name = ?"',
        context="db = get_db()",
    )
    return Batch(hunks=[hunk], token_estimate=50)


VALID_LLM_RESPONSE = """
[
  {
    "file": "src/auth.py",
    "line_start": 10,
    "line_end": 12,
    "severity": "error",
    "category": "security",
    "title": "SQL injection risk",
    "body": "User input is interpolated directly into the query string.",
    "suggested_fix": "Use a parameterised query instead."
  }
]
"""


def make_api_response(text):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=text)]
    return mock_response


def test_analyze_batch_returns_review_comments():
    with patch("llm.client.call_with_retry", return_value=make_api_response(VALID_LLM_RESPONSE)):
        with patch("llm.client.load_prompt", return_value={"model": "claude-sonnet-4-20250514", "system": "review", "version": "v1.0"}):
            comments = analyze_batch(make_batch(), prompt_version="v1.0")

    assert len(comments) == 1
    assert comments[0].severity == Severity.error
    assert comments[0].category == Category.security
    assert comments[0].file == "src/auth.py"


def test_call_with_retry_retries_on_rate_limit_then_succeeds():
    mock_response = make_api_response("ok")
    with patch("llm.client.time.sleep"):
        with patch("llm.client.client.messages.create", side_effect=[
            anthropic.RateLimitError("rate limited", response=MagicMock(), body={}),
            mock_response,
        ]) as mock_create:
            result = call_with_retry(model="m", system="s", user_message="u", max_tokens=100)

    assert mock_create.call_count == 2
    assert result == mock_response


def test_call_with_retry_raises_after_exhausting_retries():
    with patch("llm.client.time.sleep"):
        with patch("llm.client.client.messages.create",
                   side_effect=anthropic.RateLimitError("rate limited", response=MagicMock(), body={})):
            with pytest.raises(anthropic.RateLimitError):
                call_with_retry(model="m", system="s", user_message="u", max_tokens=100, retries=3)
