from collections import defaultdict
from core.models import Hunk, Batch

#How big do we want the batches?
MAX_LINES_PER_BATCH = 250

def batch_hunks(hunks: list[Hunk]) -> list[Batch]:
  
  #Group the hunks into files
  file_groups = defaultdict(list)
  for hunk in hunks: file_groups[hunk.file].append(hunk)

  #Sort the hunks into batches based on the number of total lines
  batches = []
  for file, file_hunks in file_groups:
    current_batch = []
    current_lines = 0

    for hunk in file_hunks:
      hunk_lines = len(hunk.after.splitlines() + hunk.before.splitlines())
      if current_lines + hunk_lines > MAX_LINES_PER_BATCH and current_batch:
        batches.append(Batch(hunks=current_batch, token_estimate=current_lines*10))
        current_batch=[]
        current_lines=0
      current_batch.append(hunk)
      current_lines += hunk_lines
    if current_batch:
      batches.append(Batch(hunks=current_batch, token_estimate=current_lines*10))

  return batches 
