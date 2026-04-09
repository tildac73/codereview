import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from llm.prompt_loader import load_prompt


PROMPT_YAML = """\
version: "v1.0"
model: claude-sonnet-4-20250514
system: "You are a code reviewer."
temperature: 0.2
"""

ACTIVE_YAML = 'version: "v1.0"\n'


def test_load_prompt_returns_dict_for_valid_version(tmp_path):
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "v1.0.yaml").write_text(PROMPT_YAML)

    with patch("llm.prompt_loader.PROMPTS_DIR", prompts_dir):
        result = load_prompt("v1.0")

    assert result["model"] == "claude-sonnet-4-20250514"
    assert result["version"] == "v1.0"


def test_load_prompt_reads_active_version_when_none_given(tmp_path):
    prompts_dir = tmp_path / "prompts"
    config_dir = tmp_path / "config"
    prompts_dir.mkdir()
    config_dir.mkdir()
    (prompts_dir / "v1.0.yaml").write_text(PROMPT_YAML)
    (config_dir / "active_prompt.yaml").write_text(ACTIVE_YAML)

    with patch("llm.prompt_loader.PROMPTS_DIR", prompts_dir):
        with patch("llm.prompt_loader.CONFIG_DIR", config_dir):
            result = load_prompt()

    assert result["version"] == "v1.0"


def test_load_prompt_raises_for_missing_version(tmp_path):
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()

    with patch("llm.prompt_loader.PROMPTS_DIR", prompts_dir):
        with pytest.raises(FileNotFoundError):
            load_prompt("v9.9")
