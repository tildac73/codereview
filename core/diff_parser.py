from core.models import Hunk
from core.language_detector import detect_language
import typer

"""
    Parses the diff into a list of hunks (separate changes)
"""
def parse_diff(raw_diff: str) -> list[Hunk]:
    #Initiate the PatchSet (to read the diff)
    from unidiff import PatchSet, LINE_TYPE_ADDED, LINE_TYPE_REMOVED, LINE_TYPE_CONTEXT
    patch = PatchSet(raw_diff)
    hunks = []

    #Iterate over the files in the patch, skipping binary files
    for patched_file in patch:
        if patched_file.is_binary_file: continue
        file_path = patched_file.path
        language = detect_language(file_path)

        #For every change (hunk) in the patched file, we add this to the list of hunks
        for hunk in patched_file:
            before  = "".join(line.value for line in hunk if line.line_type == LINE_TYPE_REMOVED)
            after   = "".join(line.value for line in hunk if line.line_type == LINE_TYPE_ADDED)
            context = "".join(line.value for line in hunk if line.line_type == LINE_TYPE_CONTEXT)
            line_start = hunk.target_start
            line_end = hunk.target_start + hunk.target_length

            hunks.append(Hunk(
                file=file_path,
                language=language,
                before=before,
                after=after,
                context=context,
                line_start=line_start,
                line_end=line_end,
            ))
    return hunks

"""
    Gets the diff which we will analyse from Git
"""
def get_diff_from_git(ref: str) -> str:
    from subprocess import run, CalledProcessError

    #Try to run git diff - fail gracefully if we hit any errors
    try:
        result = run(
            ["git", "diff", ref],
            capture_output=True, text=True, check=True
        )
        if not result.stdout.strip():
            typer.echo(f"Warning: no diff found for ref '{ref}' — is the working tree clean?", err=True)
            raise typer.Exit(1)
        return result.stdout
    except CalledProcessError as e:
        typer.echo(f"Error: git diff failed for ref '{ref}':\n{e.stderr.strip()}", err=True)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("Error: git not found — is it installed and on your PATH?", err=True)
        raise typer.Exit(1)
