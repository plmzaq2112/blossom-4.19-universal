# Blossom Kernel (4.19.325)

Maintained Linux 4.19.325 kernel for the Xiaomi Redmi 9A family
(`blossom` platform, MediaTek MT6762/MT6765).

Devices (by codename): `dandelion`, `angelica`, `angelican`, `angelicain`,
`cattail` (plus the `blossom` recovery codename used by some device checks).

## Features

- CPU overclock: big cores 2201 MHz, little cores 1700 MHz, CCI 1248 MHz
  (2301 MHz big-core build available as an experimental variant)
- Screen-aware minimum frequency: 800/600 MHz with the screen on,
  400/300 MHz with the screen off
- Input boost: 1.2 GHz / 1.0 GHz for one second after touch or key input
- GPU: idle at 550 MHz, boost up to 850 MHz, early ramp-up at >=45% load
- I/O scheduler: mq-deadline by default
- Memory: MEMCG + /proc/zoneinfo, PSI, MGLRU, zram/lz4, simple_lmk
- Memory watermarks: min_free_kbytes ~1% of RAM, watermark_scale_factor=50
- Blossom family DT overlays: dandelion, angelica, angelican, angelicain, cattail
- AnyKernel3 package is boot-only: kernel + base DTB, dtbo is never modified

## CPU voltage

- Top OPP (2201 MHz) source setting: `CPU_DVFS_VOLT0 = 116875` (1.16875 V)
- Measured Vproc under full load: 1081250 uV (1.08125 V), adjusted by PVS/efuse
- Other OPP voltages are unchanged from the source tree; no extra undervolt

## Important: base DTB

The DTB produced by this tree can crash LK on real hardware. The build and
release packages therefore use the known-good 1020 base DTB
(`126,985 bytes`, `sha256 333cf70ce8cf6da0dd4c3326ed7dfc4965209cce02651ad164ed749ff0211732`).
A copy is kept in `build-tools/refs/1020boot.dtb`; `build_sashimi.sh` falls back
to it when the external reference is missing.
Do not package a freshly built `mt6765.dtb` into a boot image.

## Building

`build-tools/` contains the release build scripts and the helper scripts
used during development:

- `build_sashimi.sh` — defconfig + full LTO build + AnyKernel3 packaging
- `build_o3.sh` — same build with `-O3 -mcpu=cortex-a53+crc+crypto`
- `run_build.sh` — logging wrapper
- `pack_boot.py` — repack an Android boot v2 image with a new kernel/DTB
- `append_cmdline.py` / `edit_cmdline.py` — boot cmdline helpers
- `refparse.py` — Android boot image parser used to compare reference images
- `control_build.sh` — experimental control build (fixed base commit)
- `pack_oc.py` — legacy early boot repacker (superseded by `pack_boot.py`)
- `patches/` — complete patch series (22 patches) on top of the upstream
  `sashimi` branch
- `refs/1020boot.dtb` — known-good base DTB used for the release

Requirements: clang (Neutron clang 24), GNU aarch64 cross binutils,
ccache, bc, flex, zip, dtc.

## Flashing

Back up `boot` and `dtbo` before flashing, then flash the AnyKernel3 zip in
recovery (or install it with `twrp install`). The zip only writes the boot
partition.

## Credits

- Base: `zyexro/sashimi_kernel_xiaomi_blossom` (`sashimi` branch)
- CPU overclock reference: `IsHacker-kernel/android_kernel_xiaomi_blossom`
- Blossom family overlays: `MiCode/Xiaomi_Kernel_OpenSource` (`dandelion-q-oss`)

## License

GPL-2.0, as inherited from the Linux kernel and the vendor tree.
