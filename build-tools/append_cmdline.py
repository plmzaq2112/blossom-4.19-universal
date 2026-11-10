#!/usr/bin/env python3
"""append_cmdline.py in.img out.img "extra args" """
import struct, pathlib, sys
src, dst, extra = sys.argv[1], sys.argv[2], sys.argv[3]
b = bytearray(pathlib.Path(src).read_bytes())
if b[:8] != b"ANDROID!":
    sys.exit("not an android boot image")
page = struct.unpack_from("<I", b, 36)[0]
cmd = bytes(b[64:64+512]).split(b"\0")[0]
new = cmd + b" " + extra.encode()
if len(new) >= 512:
    sys.exit(f"cmdline too long: {len(new)}")
b[64:64+512] = new + b"\0" * (512 - len(new))
pathlib.Path(dst).write_bytes(b)
print("cmdline:", new.decode())
print("total", len(b), "page", page)
