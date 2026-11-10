#!/usr/bin/env python3
"""pack_boot.py BASE.img KERNEL.gz DTB OUT.img  — keep ramdisk/cmdline/AVB footer."""
import struct, pathlib, hashlib, sys

base_p, kernel_p, dtb_p, out_p = [pathlib.Path(x) for x in sys.argv[1:5]]
base = base_p.read_bytes()[:67108864]
kernel = kernel_p.read_bytes()
dtb = dtb_p.read_bytes()

ksize, kaddr, rsize, raddr, ssize, saddr, tags, page, hver = struct.unpack_from("<9I", base, 8)
rec_size, rec_off = struct.unpack_from("<IQ", base, 1632)
hsize, dsize = struct.unpack_from("<II", base, 1644)
assert page == 2048 and hver == 2, (page, hver)

def al(x): return (x + page - 1)//page*page
old_roff = al(page + ksize)
old_soff = al(old_roff + rsize)
old_recoff = al(old_soff + ssize)
old_doff = al(old_recoff + rec_size)
ramdisk = base[old_roff:old_roff+rsize]
second = base[old_soff:old_soff+ssize]
rec = base[old_recoff:old_recoff+rec_size]

koff = page
roff = al(koff + len(kernel))
soff = al(roff + len(ramdisk))
recoff = al(soff + len(second))
doff = al(recoff + len(rec))
total = 67108864
avb = base[total-64:total]
assert avb[:4] == b"AVBf"

img = bytearray(total)
hdr = bytearray(base[:page])
struct.pack_into("<I", hdr, 8, len(kernel))
struct.pack_into("<I", hdr, 16, len(ramdisk))
struct.pack_into("<I", hdr, 24, len(second))
struct.pack_into("<I", hdr, 1648, len(dtb))
img[:page] = hdr
img[koff:koff+len(kernel)] = kernel
img[roff:roff+len(ramdisk)] = ramdisk
if second: img[soff:soff+len(second)] = second
if rec: img[recoff:recoff+len(rec)] = rec
img[doff:doff+len(dtb)] = dtb
img[total-64:total] = avb
out_p.write_bytes(img)
print("wrote", out_p, len(img))
print("kernel", len(kernel), hashlib.sha256(kernel).hexdigest()[:16])
print("dtb   ", len(dtb), hashlib.sha256(dtb).hexdigest()[:16], "at", doff)
