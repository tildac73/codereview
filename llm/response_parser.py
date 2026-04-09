import json
import typer
import re
from core.models import ReviewComment, Severity, Category

"""
    Parse the response from the LLM into a list of ReviewComments
"""
def parse_response(raw_text: str, batch, prompt_version: str) -> list[ReviewComment]:

    #Extract the Json returned by the LLM into a Json string
    json_str = extract_json(raw_text)

    #Carefully load in the Json, checking for errors (None returned, malformed)
    if json_str is None:
        log_malformed(raw_text=raw_text,batch=batch)
        return []
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        log_malformed(raw_text=raw_text,batch=batch)
        return []
    
    #For every item in the Json returned, map to a ReviewComment object and append to the comment list
    comments = []
    for item in data:
        try:
            comment = ReviewComment(
                run_id=0,
                file=item["file"],
                line_start=item["line_start"],
                line_end=item["line_end"],
                severity=Severity(item["severity"]),
                category=Category(item["category"]),
                title=item["title"],
                body=item["body"],
                suggested_fix=item.get("suggested_fix"),
                prompt_version=prompt_version,
            )
            comments.append(comment)
        except (KeyError, ValueError) as e:
            log_invalid_item(item,e)
        
    return comments

"""
    Extract Json from the LLM analysis - check for common errors and adjust accordingly
"""
def extract_json(text: str) -> str | None:

    #First, try to load the Json in its most basic format
    #If it fails, pass to the next load
    try:
        json.loads(text.strip())
        return text.strip()
    except json.JSONDecodeError:
        pass

    #Match some common LLM json mistakes and strip these, then load the Json
    match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if match:
        candidate = match.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass

    match = re.search(r'\[[\s\S]*\]', text)
    if match:
        candidate = match.group(0)
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass

    return None

"""
    Log the malformed json
"""
def log_malformed(raw_text: str, batch) -> None:
    preview = raw_text[:200].replace("\n", " ")
    typer.echo(f"Warning: malformed LLM response (preview): {preview!r}", err=True)

"""
    Log that the Json item was invalid
"""
def log_invalid_item(item: dict, e: Exception) -> None:
    typer.echo(f"Warning: skipping invalid item — {e}", err=True)
    typer.echo(f"Item: {str(item)[:200]}", err=True)