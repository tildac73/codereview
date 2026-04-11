# codereview

An LLM-powered code review CLI and visual dashboard.

## Quickstart

```bash
# Install
pip install -e .

# Set your API key
cp .env.example .env
# edit .env with your ANTHROPIC_API_KEY

# Run a review
codereview --diff HEAD~1
```