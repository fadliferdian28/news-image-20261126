#!/usr/bin/env python3
"""Copy entry.png to the output directory, verifying it byte-for-byte.

Stdlib only (hashlib, os, shutil, struct, sys). The image is the entry
itself: a one-page summary of the world's news of Thursday 26 November
2026, drawn procedurally. The program writes the same bytes on every run.
"""
import hashlib
import os
import shutil
import struct
import sys

EXPECTED_SHA256 = "fc8a4bf3bfb2bd39dbd5cbe164107fb0388ebfcb9de814085c6e3749f64c8e26"
EXPECTED_SIZE = 153674


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not os.path.isdir(out_dir):
        try:
            os.makedirs(out_dir, exist_ok=True)
        except OSError:
            out_dir = "out"
            os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")

    with open(src, "rb") as f:
        data = f.read()
    if len(data) != EXPECTED_SIZE:
        print(f"entry.png size {len(data)} != expected {EXPECTED_SIZE}", file=sys.stderr)
        return 1
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("entry.png is not a PNG", file=sys.stderr)
        return 1
    if data[8:16] != b"\x00\x00\x00\x0dIHDR":
        print("entry.png has a bad IHDR chunk header", file=sys.stderr)
        return 1
    if data[-12:] != b"\x00\x00\x00\x00IEND\xaeB`\x82":
        print("entry.png is truncated: missing IEND chunk", file=sys.stderr)
        return 1
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1024, 1024):
        print(f"entry.png is {width}x{height}, expected 1024x1024", file=sys.stderr)
        return 1
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        print(f"entry.png sha256 {digest} != expected {EXPECTED_SHA256}", file=sys.stderr)
        return 1

    # Pre-copy writability probe: fail before touching the destination.
    probe = os.path.join(out_dir, ".makefun_write_probe")
    try:
        with open(probe, "wb") as pf:
            pf.write(b"ok")
        os.remove(probe)
    except OSError as exc:
        print(f"output dir {out_dir} is not writable: {exc}", file=sys.stderr)
        return 1

    if os.path.abspath(src) == os.path.abspath(dst):
        raise shutil.SameFileError("source and destination are the same file")
    with open(dst, "wb") as f:
        f.write(data)
    print(f"wrote {dst} ({len(data)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
