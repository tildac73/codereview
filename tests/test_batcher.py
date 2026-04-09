import pytest
from core.batcher import batch_hunks, MAX_LINES_PER_BATCH
from core.models import Hunk

def make_hunk(file="src/foo.py", language="python", lines=10):
    content = "\n".join(f"line {i}" for i in range(lines))
    return Hunk(file=file, language=language, line_start=1, line_end=lines, before=content, after=content, context="")

def test_hunks_from_same_file_grouped_into_one_batch():
    hunks = [make_hunk(file="src/foo.py"), make_hunk(file="src/foo.py")]
    batches = batch_hunks(hunks)
    assert len(batches) == 1
    assert len(batches[0].hunks) == 2

def test_oversized_file_split_into_multiple_batches():
    # Each hunk has MAX_LINES_PER_BATCH lines on each side — guaranteed to exceed the limit alone
    big_hunk_1 = make_hunk(file="src/big.py", lines=MAX_LINES_PER_BATCH)
    big_hunk_2 = make_hunk(file="src/big.py", lines=MAX_LINES_PER_BATCH)
    batches = batch_hunks([big_hunk_1, big_hunk_2])
    assert len(batches) == 2
    assert batches[0].hunks == [big_hunk_1]
    assert batches[1].hunks == [big_hunk_2]

def test_empty_input_returns_empty_list():
    assert batch_hunks([]) == []
