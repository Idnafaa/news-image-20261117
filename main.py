"""News-image entry for 17 November 2026 (Python 3.13, stdlib only).

The poster itself lives in this repository as entry.png, drawn by
render.py from the day's reported news. This program does one thing:
it copies that image to the grader's output directory as entry.png.
No network, no clock, no randomness, so two runs write identical
bytes. Run locally with MAKEFUN_OUTPUT_DIR=out python3 main.py.
"""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

OUT.mkdir(parents=True, exist_ok=True)
# The copy is byte for byte: same file in, same file out, every run.
shutil.copyfile(HERE / "entry.png", OUT / "entry.png")
