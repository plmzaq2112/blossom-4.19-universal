#!/bin/bash
# Local (WSL) adaptation of bn (6).sh for the sashimi tree.
# All paths live inside ~/kernel-oc; nothing outside is touched.
set -u

KERNEL_DIR="$HOME/kernel-oc/sashimi_kernel_xiaomi_blossom"
TOOLCHAINS="$HOME/kernel-oc/toolchains"
CLANG_DIR="$TOOLCHAINS/neutron-clang"
anykernel="$HOME/kernel-oc/anykernel/AnyKernel3"
CCACHE_DIR_LOCAL="$HOME/kernel-oc/ccache"
CONFIG_FILE="blossom_defconfig"
ARCH="arm64"
JOBS="$(nproc --all)"

cd "$KERNEL_DIR" || exit 1

# --- proxy for downloads (xray on Windows host) ---
if [ -f "$HOME/kernel-oc/proxy.sh" ]; then . "$HOME/kernel-oc/proxy.sh"; fi

mkdir -p "$TOOLCHAINS" "$CCACHE_DIR_LOCAL"

# --- toolchain: Neutron clang taken from the original script ---
if [ ! -x "$CLANG_DIR/bin/clang" ]; then
  echo ">>> fetching Neutron clang into $CLANG_DIR"
  mkdir -p "$CLANG_DIR" && cd "$CLANG_DIR" || exit 1
  if [ ! -x antman ]; then
    curl -fsSL -o antman "https://raw.githubusercontent.com/Neutron-Toolchains/antman/main/antman" || exit 1
    chmod +x antman
  fi
  ./antman -S || { echo "!! antman failed"; exit 1; }
  cd "$KERNEL_DIR" || exit 1
fi

if [ -x "$CLANG_DIR/bin/clang" ]; then
  export PATH="$CLANG_DIR/bin:$PATH"
  CC_BIN="$(command -v clang)"
else
  echo "!! neutron clang missing, falling back to system clang"
  CC_BIN="$(command -v clang)"
fi
echo ">>> using clang: $CC_BIN"
"$CC_BIN" --version | head -2

export ARCH="$ARCH"
export KBUILD_BUILD_USER="t.me"
export KBUILD_BUILD_HOST="AnymoreProject"
export USE_CCACHE=1
export CCACHE_DIR="$CCACHE_DIR_LOCAL"
export CCACHE="$(command -v ccache)"

objdir="$KERNEL_DIR/out"

# --- host build strings (equivalent of the mkcompile_h sed, without dirtying the tree) ---
export KBUILD_BUILD_USER="xc112lg_+_zyexro"
export KBUILD_BUILD_HOST="crave.io"

echo ">>> make O=out mrproper"
make O="$objdir" mrproper >/dev/null 2>&1 || echo "!! mrproper had issues, continuing"
mkdir -p "$objdir"

echo ">>> generating $CONFIG_FILE (O=out)"
make -s ARCH="$ARCH" O="$objdir" "$CONFIG_FILE" || { echo "!! defconfig failed"; exit 1; }

echo ">>> starting compile: -j$JOBS KCFLAGS=${EXTRA_KCFLAGS:-<default>}"
BUILD_START=$(date +%s)
answers=$'2\ny\ny\ny\ny\ny\ny\n'
echo "$answers" | make -j"$JOBS" \
    O="$objdir" \
    ARCH="arm64" \
    SUBARCH="arm64" \
    DTC_EXT="dtc" \
    CLANG_TRIPLE="aarch64-linux-gnu-" \
    CROSS_COMPILE="aarch64-linux-gnu-" \
    CROSS_COMPILE_ARM32="arm-linux-gnueabi-" \
    CROSS_COMPILE_COMPAT="arm-linux-gnueabi-" \
    LD="ld.lld" \
    AR="llvm-ar" \
    NM="llvm-nm" \
    STRIP="llvm-strip" \
    OBJCOPY="llvm-objcopy" \
    OBJDUMP="llvm-objdump" \
    READELF="llvm-readelf" \
    HOSTCC="clang" \
    HOSTCXX="clang++" \
    HOSTAR="llvm-ar" \
    HOSTLD="ld.lld" \
    LLVM=1 \
    LLVM_IAS=1 \
    KCFLAGS="${EXTRA_KCFLAGS:-}" \
    CC="ccache clang"
rc=$?
BUILD_END=$(date +%s)
echo ">>> make exited with $rc after $((BUILD_END-BUILD_START))s"
[ $rc -ne 0 ] && exit $rc

# --- outputs ---
image="$objdir/arch/arm64/boot/Image"
dtb_img="$objdir/arch/arm64/boot/dtb.img"
outdir="$KERNEL_DIR/newkernel"
mkdir -p "$outdir"

[ -f "$image" ] || { echo "!! no Image produced"; exit 1; }
cp "$image" "$outdir/kernel"
gzip -9 -f "$outdir/kernel"
mv "$outdir/kernel.gz" "$outdir/kernel"

# NOTE: the DTB produced by this tree does not boot on this unit (LK crashes while
# loading it).  The known-good DTB is the one from the 1020 stock boot image.
REF_DTB="$HOME/kernel-oc/logs/refs/1020boot.dtb"
if [ -f "$REF_DTB" ]; then
  cp "$REF_DTB" "$outdir/dtb.img"
  echo ">>> dtb from known-good reference: $REF_DTB"
else
  echo "!! WARNING: $REF_DTB missing, falling back to freshly built DTB (may not boot)"
  for cand in "$dtb_img" "$objdir/arch/arm64/boot/mtk.dtb" \
              "$objdir/arch/arm64/boot/dts/mediatek/mt6765.dtb"; do
    if [ -f "$cand" ]; then cp "$cand" "$outdir/dtb.img"; echo ">>> dtb from $cand"; break; fi
  done
fi
ls -lh "$outdir"

# --- AnyKernel3 zip ---
if [ ! -f "$anykernel/tools/ak3-core.sh" ]; then
  mkdir -p "$(dirname "$anykernel")"
  git -c http.proxy="${http_proxy:-}" clone --depth=1 https://github.com/osm0sis/AnyKernel3 "$anykernel" || exit 1
fi
cd "$anykernel" || exit 1
rm -f Image Image.gz Image.gz-dtb dtb *.zip
gzip -9 -c "$image" > Image.gz
[ -f "$outdir/dtb.img" ] && cp "$outdir/dtb.img" dtb

cat > anykernel.sh <<'AKEOF'
### AnyKernel3 Ramdisk Mod Script
properties() { '
kernel.string=Blossom kernel
do.devicecheck=1
do.modules=0
do.systemless=0
do.cleanup=1
do.cleanuponabort=0
device.name1=blossom
device.name2=dandelion
device.name3=angelica
device.name4=angelican
device.name5=angelicain
device.name6=cattail
supported.versions=
supported.patchlevels=
supported.vendorpatchlevels=
'; }

BLOCK=/dev/block/by-name/boot;
IS_SLOT_DEVICE=0;
RAMDISK_COMPRESSION=auto;
PATCH_VBMETA_FLAG=auto;

. tools/ak3-core.sh;

# (backup left to the user: back up boot + dtbo before flashing)
split_boot;
flash_boot;
AKEOF

ZIPNAME="Blossom-Kernel-$(date +%Y%m%d-%H%M).zip"
zip -r9 "$ZIPNAME" . -x ".git*" "README*" "*.md" "*.zip" >/dev/null || exit 1
mkdir -p "$KERNEL_DIR/newkernel"
cp "$ZIPNAME" "$KERNEL_DIR/newkernel/"
echo ">>> flashable zip: $KERNEL_DIR/newkernel/$ZIPNAME"
cd "$KERNEL_DIR" || exit 1
