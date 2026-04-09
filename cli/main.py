import typer
import hashlib
import json
from typing import Optional
from pathlib import Path

app = typer.Typer()

"""
   The main app loop, executes the entire workflow from reading CLI and delegating tasks around files, 
   to then rendering output
"""
@app.command()
def review(
    diff: str = typer.Option(..., help="Git ref like HEAD~1, or path to a .diff file"),
    pr: str = typer.Option(None, help="Github PR URL"),
    file_filter: str = typer.Option(None, "--file", help="Only review this file"),
    prompt_version: str = typer.Option(None, help="Override active prompt version"),
    output: str = typer.Option("terminal", help="terminal | json | server"),
):

   #Check for any errors and in CLI and fail if present
   if not diff and not pr:
      typer.echo("Error: provide either --diff or --pr", err=True)
      raise typer.Exit(1)
   if diff and pr:
      typer.echo("Error: --diff and --pr are mutually exclusive", err=True)
      raise typer.Exit(1)
   if file_filter and not diff:
      typer.echo("Error: --file requires --diff", err=True)
      raise typer.Exit(1)

   #Get the diff from git
   #TODO: implement get PR diff
   if diff:
      raw_diff = get_diff_from_git(diff)
   else:
      typer.echo("--pr not yet implemented", err=True)
      raise typer.Exit(1)
   
   #Parse the diff into smaller hunks so we don't overload the Claude prompt buffer
   hunks = parse_diff(raw_diff)
   if file_filter:
     hunks = [h for h in hunks if h.file == file_filter]

   batches = batch_hunks(hunks)

   #Send to Claude to analyse the diff in batches, and save these to all_comments
   all_comments = []
   for batch in batches:
    all_comments.extend(analyze_batch(batch, prompt_version))

   #Construct a run object for the code review, including a unique run hash
   git_ref = diff or pr
   raw_diff_hash = hashlib.sha256(raw_diff.encode()).hexdigest()
   run = Run(
     git_ref=git_ref,
     prompt_version=prompt_version or "v1.0",
     total_comments=len(all_comments),
     raw_diff_hash=raw_diff_hash
   )
   save_run(run,all_comments)

   #Output the review how the user specifies
   if output == "terminal":
      render_terminal(all_comments)
   elif output == "json":
      typer.echo(json.dumps([c.model_dump() for c in all_comments], indent=2))
   elif output == "server":
      import uvicorn
      from api.server import app as api_app
      uvicorn.run(api_app, host="0.0.0.0", port=8000)
   else:
      typer.echo(f"Error: unknown output format '{output}'", err=True)
      raise typer.Exit(1)

"""
   This function is responsible for rendering code review output in the terminal
"""
def render_terminal(comments):
   from collections import defaultdict
   from rich.console import Console
   from rich.table import Table
   from rich import box
   from rich.panel import Panel

   console = Console()

   #Colour coding the terminal output
   SEVERITY_STYLES = {
      "error": "bold red",
      "warning": "yellow",
      "suggestion": "blue",
      "nitpick": "dim white",
   }

   #Sort all comments by file
   by_file = defaultdict(list)
   for c in comments:
      by_file[c.file].append(c)

   counts = defaultdict(int)

   for filename, file_comments in by_file.items():
      console.print(f"\n[bold]{filename}[/bold]")

      table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold cyan")
      table.add_column("Line",style="dim",width=6)
      table.add_column("Severity",width=12)
      table.add_column("Category",width=14)
      table.add_column("Title")

      for c in file_comments:
         style = SEVERITY_STYLES.get(c.severity, "")
         counts[c.severity] += 1
         table.add_row(
               str(c.line),
               f"[{style}]{c.severity}[/{style}]",
               c.category,
               c.title,
               style=style,
         )

      console.print(table)
   n_files = len(by_file)
   summary = (
      f"Found [red]{counts['error']} errors[/red], "
      f"[yellow]{counts['warning']} warnings[/yellow], "
      f"[blue]{counts['suggestion']} suggestions[/blue], "
      f"[dim]{counts['nitpick']} nitpicks[/dim] "
      f"across {n_files} file{'s' if n_files != 1 else ''}"
   )
   console.print(Panel(summary, title="Summary", border_style="cyan"))


if __name__ == "__main__":
    app()