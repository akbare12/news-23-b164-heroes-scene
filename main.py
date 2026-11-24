#!/usr/bin/env python3
"""Generate entry.png for the NEWS-23 b164 heroes-scene front page.

Stdlib only (no PIL): validates the bundled PNG byte-for-byte and copies it
to MAKEFUN_OUTPUT_DIR/entry.png. The image itself is produced by draw.py;
this script only verifies and delivers it.
"""
import hashlib
import os
import struct
import sys
import zlib

EXPECTED_SHA256 = "77f1e33022e7c97033c72e648e1c6bb6f0d7b2ba9be74e4839f3ba60800a99e3"  # entry.png, 2026-11-25
EXPECTED_SIZE = 189355

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def fail(msg):
    print("error: " + msg, file=sys.stderr)
    sys.exit(1)


def check_png(data):
    if len(data) < 8 or data[:8] != b"\x89PNG\r\n\x1a\n":
        fail("bad PNG signature")
    if len(data) < 10_000:
        fail("PNG too small (%d bytes)" % len(data))
    if len(data) > 1_048_576:
        fail("PNG over 1 MiB (%d bytes)" % len(data))
    # first chunk must be IHDR, 13 bytes, 1024x1024, 8-bit, colour type 2/6
    if len(data) < 33:
        fail("PNG truncated before IHDR")
    ln, typ = struct.unpack(">I4s", data[8:16])
    if typ != b"IHDR" or ln != 13:
        fail("first chunk is not a 13-byte IHDR")
    w, h, depth, ctype, comp, filt, inter = struct.unpack(">IIBBBBB", data[16:29])
    if (w, h) != (1024, 1024):
        fail("wrong dimensions %dx%d (want 1024x1024)" % (w, h))
    if depth != 8 or ctype not in (2, 6):
        fail("unsupported bit depth %d / colour type %d" % (depth, ctype))
    if comp != 0 or filt != 0 or inter != 0:
        fail("unsupported compression/filter/interlace")
    ihdr_crc = zlib.crc32(b"IHDR" + data[16:29]) & 0xFFFFFFFF
    stored = struct.unpack(">I", data[29:33])[0]
    if ihdr_crc != stored:
        fail("IHDR CRC mismatch")
    # walk chunks: CRC each, IDAT non-empty, IEND last with no trailing data
    off = 8
    idat_total = 0
    seen_iend = False
    while off < len(data):
        if off + 8 > len(data):
            fail("truncated chunk header")
        ln, typ = struct.unpack(">I4s", data[off:off + 8])
        end = off + 8 + ln + 4
        if end > len(data):
            fail("truncated chunk %r" % typ)
        crc = zlib.crc32(typ + data[off + 8:off + 8 + ln]) & 0xFFFFFFFF
        stored = struct.unpack(">I", data[off + 8 + ln:end])[0]
        if crc != stored:
            fail("CRC mismatch in chunk %r" % typ)
        if typ == b"IDAT":
            if ln == 0:
                fail("empty IDAT chunk")
            idat_total += ln
        if typ == b"IEND":
            if ln != 0:
                fail("IEND must be empty")
            if end != len(data):
                fail("trailing data after IEND")
            seen_iend = True
            break
        off = end
    if not seen_iend:
        fail("missing IEND chunk")
    if idat_total < 1000:
        fail("IDAT payload too small (%d bytes)" % idat_total)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    if not outdir:
        fail("MAKEFUN_OUTPUT_DIR is empty")
    if os.path.isfile(outdir):
        fail("MAKEFUN_OUTPUT_DIR is a file, not a directory")
    outdir_abs = os.path.abspath(outdir)
    here_abs = os.path.abspath(HERE)
    if outdir_abs == here_abs or outdir_abs.startswith(here_abs + os.sep):
        fail("MAKEFUN_OUTPUT_DIR must be outside the repo")
    if not os.path.exists(SOURCE):
        fail("source entry.png missing next to main.py")
    with open(SOURCE, "rb") as f:
        data = f.read()
    check_png(data)
    if EXPECTED_SIZE and len(data) != EXPECTED_SIZE:
        fail("size mismatch: got %d, expected %d" % (len(data), EXPECTED_SIZE))
    sha = hashlib.sha256(data).hexdigest()
    if EXPECTED_SHA256 and sha != EXPECTED_SHA256:
        fail("sha256 mismatch: got %s" % sha)
    os.makedirs(outdir_abs, exist_ok=True)
    dst = os.path.join(outdir_abs, "entry.png")
    if os.path.abspath(dst) == os.path.abspath(SOURCE):
        fail("output would overwrite the source image")
    with open(dst, "wb") as f:
        f.write(data)
    with open(dst, "rb") as f:
        back = f.read()
    if back != data:
        fail("re-read mismatch after write")
    print("wrote %s (%d bytes, sha256 %s)" % (dst, len(data), sha))


if __name__ == "__main__":
    main()
