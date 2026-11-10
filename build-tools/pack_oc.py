#!/usr/bin/env python3
"""Repack Android boot v2: keep current ramdisk/cmdline/AVB footer,
replace kernel with the OC Image.gz and dtb with the known-good 1020 dtb.
Everything stays inside ~/kernel-oc.
"""
import struct, pathlib, hashlib, sys

root = pathlib.Path.home()/"kernel-oc"
base = (root/"logs/boot.img").read_bytes()[:67108864]   # strip adb noise
new_kernel = (root/"sashimi_kernel_xiaomi_blossom/newkernel/kernel").read_bytes()
new_dtb = (root/"logs/refs/1020boot.dtb").read_bytes()

ksize, kaddr, rsize, raddr, ssize, saddr, tags, page, hver = struct.unpack_from("<9I", base, 8)
rec_size, rec_off = struct.unpack_from("<IQ", base, 1632)
hsize, dsize = struct.unpack_from("<II", base, 1644)
assert page == 2048 and hver == 2

def al(x): return (x + page - 1)//page*page
old_koff = page
old_roff = al(old_koff + ksize)
old_soff = al(old_roff + rsize)
old_recoff = al(old_soff + ssize)
old_doff = al(old_recoff + rec_size)
ramdisk = base[old_roff:old_roff+rsize]
second  = base[old_soff:old_soff+ssize]
rec     = base[old_recoff:old_recoff+rec_size]
print("old layout: k@%d r@%d s@%d rec@%d dtb@%d" % (old_koff, old_roff, old_soff, old_recoff, old_doff))
print("old ramdisk sha", hashlib.sha256(ramdisk).hexdigest()[:16])
print("old dtb sha", hashlib.sha256(base[old_doff:old_doff+dsize]).hexdigest()[:16])

# new layout
koff = page
roff = al(koff + len(new_kernel))
soff = al(roff + len(ramdisk))
recoff = al(soff + len(second))
doff = al(recoff + len(rec))
total = 67108864
avb = base[total-64:total]
assert avb[:4] == b"AVBf", avb[:8]
print("new layout: k@%d r@%d dtb@%d  (k=%d dtb=%d)" % (koff, roff, doff, len(new_kernel), len(new_dtb)))

img = bytearray(b"\0" * total)
hdr = bytearray(base[:page])
struct.pack_into("<I", hdr, 8, len(new_kernel))
struct.pack_into("<I", hdr, 16, len(ramdisk))
struct.pack_into("<I", hdr, 24, len(second))
struct.pack_into("<I", hdr, 1648, len(new_dtb))
img[0:page] = hdr
img[koff:koff+len(new_kernel)] = new_kernel
img[roff:roff+len(ramdisk)] = ramdisk
if second: img[soff:soff+len(second)] = second
if rec: img[recoff:recoff+len(rec)] = rec
img[doff:doff+len(new_dtb)] = new_dtb
img[total-64:total] = avb

out = root/"logs/boot_oc_1020dtb.img"
out.write_bytes(img)
print("wrote", out, len(img))
print("sha", hashlib.sha256(img).hexdigest())

# verify
v = out.read_bytes()
ks, _, rs, _, ss, _, _, pg, hv = struct.unpack_from("<9I", v, 8)
rc, _ = struct.unpack_from("<IQ", v, 1632)
hs, ds = struct.unpack_from("<II", v, 1644)
ko, ro = pg, al(pg+ks)
so = al(ro+rs); rco = al(so+ss); do = al(rco+rc)
print("verify: kernel_ok", v[ko:ko+ks] == new_kernel, "ramdisk_ok", v[ro:ro+rs] == ramdisk,
      "dtb_ok", v[do:do+ds] == new_dtb, "dtb_size", ds)
