#!/bin/bash
set -u
K="$HOME/kernel-oc/sashimi_kernel_xiaomi_blossom"
CL="$HOME/kernel-oc/toolchains/neutron-clang"
export PATH="$CL/bin:$PATH"
export ARCH=arm64
export CCACHE_DIR="$HOME/kernel-oc/ccache"
cd "$K" || exit 1
git checkout -f -B control-sashimi 864ecc0c4 2>&1 | tail -2
make -j"$(nproc)" \
  O=out ARCH=arm64 SUBARCH=arm64 DTC_EXT=dtc \
  CLANG_TRIPLE=aarch64-linux-gnu- CROSS_COMPILE=aarch64-linux-gnu- \
  CROSS_COMPILE_ARM32=arm-linux-gnueabi- CROSS_COMPILE_COMPAT=arm-linux-gnueabi- \
  LD=ld.lld AR=llvm-ar NM=llvm-nm STRIP=llvm-strip OBJCOPY=llvm-objcopy \
  OBJDUMP=llvm-objdump READELF=llvm-readelf \
  HOSTCC=clang HOSTCXX=clang++ HOSTAR=llvm-ar HOSTLD=ld.lld \
  LLVM=1 LLVM_IAS=1 CC="ccache clang"
rc=$?
echo "control build rc=$rc"
mkdir -p "$HOME/kernel-oc/logs/control"
cp -f out/arch/arm64/boot/Image.gz "$HOME/kernel-oc/logs/control/"
cp -f out/arch/arm64/boot/dts/mediatek/mt6765.dtb "$HOME/kernel-oc/logs/control/"
ls -l "$HOME/kernel-oc/logs/control/"
