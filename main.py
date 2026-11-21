#!/usr/bin/env python3
"""LUMIVALE — The Poster for a Place That Isn't There (acct3).

Copies the entry poster (entry.png, JPEG content, 1024x1024) from this
repository into the output directory as entry.png, validating size and
dimensions first, then verifying the copy byte-for-byte.
"""

import os
import shutil
import struct
import sys
from pathlib import Path

MAX_BYTES = 1_048_576
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024


def image_dimensions(path):
    """Return (width, height) for a PNG or JPEG file, stdlib-only."""
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", data[16:24])
        return width, height
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 1:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                height, width = struct.unpack(">HH", data[i + 5:i + 9])
                return width, height
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            i += 2 + length
    raise ValueError("unsupported image format (expected PNG or JPEG)")


def validate(src):
    size = src.stat().st_size
    if size == 0:
        raise SystemExit("entry.png is empty")
    if size > MAX_BYTES:
        raise SystemExit(
            f"entry.png too large: {size} bytes (max {MAX_BYTES})"
        )
    width, height = image_dimensions(src)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise SystemExit(
            f"entry.png dimensions {width}x{height}, "
            f"expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}"
        )
    return size, width, height


def verify_copy(src, dest):
    """Byte-for-byte round-trip check between repo image and output."""
    if not dest.is_file():
        raise SystemExit("round-trip check failed: output file missing")
    if dest.stat().st_size != src.stat().st_size:
        raise SystemExit("round-trip check failed: output size differs")
    if dest.read_bytes() != src.read_bytes():
        raise SystemExit("round-trip check failed: output differs from entry.png")


def main():
    here = Path(__file__).resolve().parent
    src = here / "entry.png"
    if not src.is_file():
        raise SystemExit("entry.png not found next to main.py")
    size, width, height = validate(src)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"
    shutil.copyfile(src, dest)
    verify_copy(src, dest)
    print(f"wrote entry.png ({size} bytes, {width}x{height})")


if __name__ == "__main__":
    main()
