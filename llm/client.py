import anthropic
import json
import time
from core.models import Batch, ReviewComment
from llm.prompt_loader import load_prompt
from llm.response_parser import parse_response

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

def analyze_batch(batch: Batch, prompt_version: str = None) -> list[ReviewComment]:
    #Load the prompt to send to the LLM
    prompt_config = load_prompt(prompt_version)

    hunk_sections = []
    for hunk in batch.hunks:
        hunk_sections.append(
            f"### File: {hunk.file} ({hunk.language}) — Lines {hunk.line_start}-{hunk.line_end}\n"
            f"REMOVED:\n{hunk.before}\n"
            f"ADDED:\n{hunk.after}\n"
            f"CONTEXT:\n{hunk.context}"
        )
    formatted_diff = "\n\n".join(hunk_sections)

    response = call_with_retry(
        model=prompt_config["model"],
        system=prompt_config["system"],
        user_message=formatted_diff,
        max_tokens=1000
    )

    raw_text = response.content[0].text

    comments = parse_response(raw_text, batch, prompt_config["version"])

    return comments


def call_with_retry(model, system, user_message, max_tokens, retries=3):
    for attempt in range(retries):
        try:
            return client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_message}]
            )
        except anthropic.RateLimitError:
            if attempt == retries - 1: raise
            time.sleep(2 ** attempt)
        except anthropic.APIError as e:
            raise