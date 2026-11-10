#!/usr/bin/env python3
"""edit_cmdline.py in.img out.img remove_prefix"""
import struct, pathlib, sys
src, dst, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
b = bytearray(pathlib.Path(src).read_bytes())
if b[:8] != b"ANDROID!":
    sys.exit("not boot image")
cmd = bytes(b[64:64+512]).split(b"\0")[0].decode()
parts = [p for p in cmd.split() if not p.startswith(prefix)]
new = " ".join(parts).encode()
b[64:64+512] = new + b"\0" * (512 - len(new))
pathlib.Path(dst).write_bytes(b)
print("cmdline:", new.decode())
