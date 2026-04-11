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

# Start the visual dashboard
codereview --diff HEAD~1 --output server
# then open http://localhost:8000
```

## Run evals
```bash
python -m evals.runner --prompt-version v1.0
```

## Project structure
See the pseudocode in each file for implementation guidance.
Build order: models → diff_parser → batcher → llm/client → storage → api → frontend → evals
