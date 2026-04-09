from core.models import Severity, Category
from llm.response_parser import parse_response


def make_batch():
    from core.models import Batch, Hunk
    hunk = Hunk(file="src/auth.py", language="python", line_start=1, line_end=5,
                before="old", after="new", context="")
    return Batch(hunks=[hunk], token_estimate=10)


VALID_JSON = """
[
  {
    "file": "src/auth.py",
    "line_start": 10,
    "line_end": 12,
    "severity": "error",
    "category": "security",
    "title": "SQL injection risk",
    "body": "User input interpolated into query.",
    "suggested_fix": "Use parameterised queries."
  }
]
"""


def test_parse_response_returns_comments_from_valid_json():
    comments = parse_response(VALID_JSON, make_batch(), "v1.0")

    assert len(comments) == 1
    assert comments[0].severity == Severity.error
    assert comments[0].category == Category.security
    assert comments[0].prompt_version == "v1.0"


def test_parse_response_returns_empty_list_on_malformed_json():
    comments = parse_response("this is not json at all", make_batch(), "v1.0")

    assert comments == []


def test_parse_response_skips_invalid_items_keeps_valid_ones():
    mixed_json = """
    [
      {"missing": "all required fields"},
      {
        "file": "src/auth.py",
        "line_start": 1,
        "line_end": 2,
        "severity": "warning",
        "category": "logic",
        "title": "Null check missing",
        "body": "Value may be None here."
      }
    ]
    """
    comments = parse_response(mixed_json, make_batch(), "v1.0")

    assert len(comments) == 1
    assert comments[0].title == "Null check missing"
