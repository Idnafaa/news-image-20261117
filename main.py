"""news-image-20261117 v4 entry program (Python 3.13, stdlib only).

Copies the poster held in this repository to the harness output
directory as entry.png. No network, no clock, no randomness: the
bytes copied are always the same, so repeated runs are identical.
The harness may set MAKEFUN_OUTPUT_DIR; otherwise /output is used.
"""
import os
import shutil
from pathlib import Path

SRC = Path(__file__).resolve().parent / "entry.png"
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")) / "entry.png"

OUT.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(SRC, OUT)
print("wrote", OUT)
