"""news-image-20261117 v3 entry program (Python 3.13, stdlib only).

Copies the poster held in this repository to the harness output
directory as entry.png. No network, no clock, no randomness: the
bytes copied are always the same, so repeated runs are identical.
The harness may set MAKEFUN_OUTPUT_DIR; otherwise /output is used.
"""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEST = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")) / "entry.png"

DEST.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(HERE / "entry.png", DEST)
print("wrote", DEST)
