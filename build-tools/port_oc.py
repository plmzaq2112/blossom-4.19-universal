#!/usr/bin/env python3
"""Port IsHacker-kernel's CPU overclock to the sashimi tree.

IsHacker final state (branch master @0d7457d08):
  C62/C62LY  L  2101 -> 2201 MHz @ Vproc 120 (1168750 uV in opp table)
             LL 1500 -> 1700 MHz @ Vproc 120
             CCI 1048 -> 1248 MHz @ Vproc 120
  mt6765.dts: cluster0 2401 -> 2501 MHz, cluster1 1800 -> 2000 MHz, CCI 1051 -> 1251 MHz
GPU OC is deliberately NOT touched: sashimi already runs 850/690/550 MHz
(IsHacker only does 680/520/416).
"""
import sys, pathlib

root = pathlib.Path.home() / "kernel-oc" / "sashimi_kernel_xiaomi_blossom"
changed = []

def sub_any(path, olds, new, count=1):
    p = root / path
    s = p.read_text()
    for old in olds:
        if s.count(old) >= count:
            p.write_text(s.replace(old, new, count))
            changed.append((path, old, new))
            return
    sys.exit(f"FAIL {path}: none of {olds!r} found")

def sub_in_block(path, start_marker, end_marker, old, new):
    p = root / path
    s = p.read_text()
    i = s.index(start_marker)
    j = s.index(end_marker, i)
    block = s[i:j]
    if block.count(old) < 1:
        sys.exit(f"FAIL {path} [{start_marker}]: {old!r} not found")
    p.write_text(s[:i] + block.replace(old, new, 1) + s[j:])
    changed.append((path + " [" + start_marker + "]", old, new))

OPP = "drivers/misc/mediatek/base/power/cpufreq_v1/src/mach/mt6765/mtk_cpufreq_opp_table.h"
PV  = "drivers/misc/mediatek/base/power/cpufreq_v1/src/mach/mt6765/mtk_cpufreq_opp_pv_table.h"
DTS = "arch/arm64/boot/dts/mediatek/mt6765.dts"

# 1. static tables used by the v1 cpufreq driver
for suffix in ("C62", "C62LY"):
    sub_any(OPP, [f"#define CPU_DVFS_FREQ0_L_{suffix}    2101000"], f"#define CPU_DVFS_FREQ0_L_{suffix}    2201000")
    sub_any(OPP, [f"#define CPU_DVFS_FREQ0_LL_{suffix}    1500000"], f"#define CPU_DVFS_FREQ0_LL_{suffix}    1700000")
    sub_any(OPP, [f"#define CPU_DVFS_FREQ0_CCI_{suffix}    1048000"], f"#define CPU_DVFS_FREQ0_CCI_{suffix}    1248000")
    sub_any(OPP, [f"#define CPU_DVFS_VOLT0_VPROC_L_{suffix}    106875",
                  f"#define CPU_DVFS_VOLT0_VPROC_L_{suffix}    111875"],
            f"#define CPU_DVFS_VOLT0_VPROC_L_{suffix}    116875")
    sub_any(OPP, [f"#define CPU_DVFS_VOLT0_VPROC_LL_{suffix}    102500",
                  f"#define CPU_DVFS_VOLT0_VPROC_LL_{suffix}    111875"],
            f"#define CPU_DVFS_VOLT0_VPROC_LL_{suffix}    116875")
    sub_any(OPP, [f"#define CPU_DVFS_VOLT0_VPROC_CCI_{suffix}    106875",
                  f"#define CPU_DVFS_VOLT0_VPROC_CCI_{suffix}    111875"],
            f"#define CPU_DVFS_VOLT0_VPROC_CCI_{suffix}    116875")

# 2. PV / hybrid tables
for start, end in (("static unsigned int c62Tbl", "static unsigned int c62lyTbl"),
                   ("static unsigned int c62lyTbl", "unsigned int *xrecordTbl")):
    sub_in_block(PV, start, end, "{ 2101, 96, 1, 1 }", "{ 2201, 120, 1, 1 }")
    sub_in_block(PV, start, end, "{ 1500, 96, 2, 1 }", "{ 1700, 120, 2, 1 }")
    sub_in_block(PV, start, end, "{ 1048, 96, 2, 1 }", "{ 1248, 120, 2, 1 }")

# 3. devicetree OPP tables
sub_any(DTS, ["\t\t\topp-hz = /bits/ 64 <2401000000>;\n\t\t\topp-microvolt = <1068750>;"],
        "\t\t\topp-hz = /bits/ 64 <2501000000>;\n\t\t\topp-microvolt = <1168750>;")
sub_any(DTS, ["\t\t\topp-hz = /bits/ 64 <1800000000>;\n\t\t\topp-microvolt = <1025000>;"],
        "\t\t\topp-hz = /bits/ 64 <2000000000>;\n\t\t\topp-microvolt = <1168750>;")
sub_any(DTS, ["\t\t\topp-hz = /bits/ 64 <1051000000>;\n\t\t\topp-microvolt = <1068750>;"],
        "\t\t\topp-hz = /bits/ 64 <1251000000>;\n\t\t\topp-microvolt = <1168750>;")
sub_any(DTS, ["clock-frequency = <2401000000>;"], "clock-frequency = <2501000000>;", 4)
sub_any(DTS, ["clock-frequency = <1800000000>;"], "clock-frequency = <2000000000>;", 4)

print(f"{len(changed)} replacements applied:")
for path, old, new in changed:
    print("  ", path.split("/")[-1], "|", old.strip(), "->", new.strip())
