import subprocess
import pytest
from unittest.mock import patch
from core.diff_parser import parse_diff, get_diff_from_git

SIMPLE_DIFF = """\
diff --git a/src/auth.py b/src/auth.py
index abc123..def456 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -10,3 +10,3 @@ def login(user, password):
     db = get_db()
-    query = f"SELECT * FROM users WHERE name = {user}"
+    query = "SELECT * FROM users WHERE name = ?"
     return cursor.fetchone()
"""

BINARY_DIFF = """\
diff --git a/assets/logo.png b/assets/logo.png
index abc123..def456 100644
Binary files a/assets/logo.png and b/assets/logo.png differ
"""

def test_parse_diff_returns_correct_hunk_fields():
    hunks = parse_diff(SIMPLE_DIFF)
    assert len(hunks) == 1
    hunk = hunks[0]
    assert hunk.file == "src/auth.py"
    assert hunk.language == "python"
    assert 'f"SELECT * FROM users WHERE name = {user}"' in hunk.before
    assert '"SELECT * FROM users WHERE name = ?"' in hunk.after

def test_parse_diff_skips_binary_files():
    hunks = parse_diff(BINARY_DIFF)
    assert hunks == []

def test_get_diff_from_git_raises_on_bad_ref():
    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(128, "git")):
        with pytest.raises(Exception):
            get_diff_from_git("bad-ref")
