#!/usr/bin/env python3
"""Emit the competition entry image.

`news.png`, stored next to this file, is the finished artwork. The grader
expects the image at <output>/entry.png, so this script performs exactly
one job: deliver those bytes, unchanged, to that location.

The output depends only on the bytes held in this repository. Nothing here
touches the network, the clock, or any random source, so repeated runs
always produce a byte-identical entry.png. The delivered file is verified
against the source with a SHA-256 digest before the script reports
success.
"""

import hashlib
import os
import sys
from pathlib import Path

IMAGE_NAME = "news.png"
ENTRY_NAME = "entry.png"
READ_BLOCK = 65536


def output_dir() -> Path:
    override = os.environ.get("MAKEFUN_OUTPUT_DIR")
    return Path(override) if override else Path("/output")


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(READ_BLOCK)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    source = Path(__file__).resolve().parent / IMAGE_NAME
    if not source.is_file():
        print(f"missing source image: {source}", file=sys.stderr)
        return 1

    dest_dir = output_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / ENTRY_NAME

    # Write to a staging name first, then rename, so a grader never sees a
    # half-written entry.png.
    staging = dest_dir / (ENTRY_NAME + ".part")
    staging.write_bytes(source.read_bytes())
    os.replace(staging, dest)

    written_digest = sha256_of(dest)
    if written_digest != sha256_of(source):
        print("verification failed: written file differs from source",
              file=sys.stderr)
        return 1
    print(f"wrote {dest} ({dest.stat().st_size} bytes, "
          f"sha256 {written_digest[:16]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
