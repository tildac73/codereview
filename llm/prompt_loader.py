import yaml
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"
CONFIG_DIR = Path(__file__).parent.parent / "config"


def load_prompt(version: str = None) -> dict:
    if version is None:
       active = yaml.safe_load((CONFIG_DIR / "active_prompt.yaml").read_text())
       version = active["version"]
    prompt_path = PROMPTS_DIR / f"{version}.yaml"
    if not prompt_path.exists():
       raise FileNotFoundError(f"Prompt version {version} not found")
    
    return yaml.safe_load(prompt_path.read_text())