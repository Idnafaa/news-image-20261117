"""news-image-20261117 v2 entry program (Python 3.13, stdlib only).

Writes the poster stored in this repository to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png when the harness sets it).
No network, no clock, no randomness: every run copies the same
bytes, so two runs are byte-identical.
"""
import os
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO / "entry.png", OUT_DIR / "entry.png")


if __name__ == "__main__":
    main()
