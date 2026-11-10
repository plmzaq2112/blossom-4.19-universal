#!/usr/bin/env python3
import struct, pathlib, hashlib, sys

def parse_boot(path):
    b = pathlib.Path(path).read_bytes()
    if b[:8] != b"ANDROID!":
        print(path, "not android boot", b[:8]); return None
    (ksize, kaddr, rsize, raddr, ssize, saddr, tags, page, hver) = struct.unpack_from("<9I", b, 8)
    cmdline = b[64:64+512].split(b"\0")[0].decode("latin1")
    rec_size, rec_off = struct.unpack_from("<IQ", b, 1632)
    hsize, dsize = struct.unpack_from("<II", b, 1644)
    dtb_addr, = struct.unpack_from("<Q", b, 1652)
    def al(x): return (x + page - 1)//page*page
    koff = page
    roff = al(koff + ksize)
    soff = al(roff + rsize)
    recoff = al(soff + ssize)
    doff = al(recoff + rec_size)
    info = dict(path=path, size=len(b), page=page, hver=hver, ksize=ksize, rsize=rsize,
                ssize=ssize, dsize=dsize, rec_size=rec_size, koff=koff, roff=roff,
                doff=doff, hsize=hsize, cmdline=cmdline)
    info["kernel"] = b[koff:koff+ksize]
    info["ramdisk"] = b[roff:roff+rsize]
    info["dtb"] = b[doff:doff+dsize] if dsize else b""
    return info

def sha(x): return hashlib.sha256(x).hexdigest()[:16]

boots = {
 "1020boot": "/mnt/c/Users/31806/Documents/opencode/dandelion-kernel/_archive/sashimi-kernel-test-20261109/Working-1107-1020DTB/1020boot.img",
 "1107boot": "/mnt/c/Users/31806/Documents/opencode/dandelion-kernel/_archive/sashimi-kernel-test-20261109/Working-1107-1020DTB/1107boot.img",
}
out = pathlib.Path.home()/"kernel-oc/logs/refs"
out.mkdir(parents=True, exist_ok=True)
for name, p in boots.items():
    i = parse_boot(p)
    if not i: continue
    print(f"== {name}: hver={i['hver']} page={i['page']} kernel={i['ksize']} ramdisk={i['rsize']} dtb={i['dsize']} rec={i['rec_size']} hs={i['hsize']}")
    print("   cmdline:", i["cmdline"][:120])
    print("   kernel sha", sha(i["kernel"]), " dtb sha", sha(i["dtb"]))
    if i["dtb"]:
        (out/f"{name}.dtb").write_bytes(i["dtb"])
    (out/f"{name}.kernel.gz").write_bytes(i["kernel"])
    (out/f"{name}.ramdisk").write_bytes(i["ramdisk"])
    (out/f"{name}.boot.img").write_bytes(pathlib.Path(p).read_bytes())

print("\n== built dtbs in out/arch/arm64/boot ==")
bd = pathlib.Path.home()/"kernel-oc/sashimi_kernel_xiaomi_blossom/out/arch/arm64/boot"
for f in sorted(list(bd.glob("*.dtb")) + list(bd.glob("*.merge")) + [bd/"dtb.img", bd/"mtk.dtb"]):
    if f.exists():
        data = f.read_bytes()
        print(f"  {f.name:24} {len(data):>8} sha={sha(data)}")
