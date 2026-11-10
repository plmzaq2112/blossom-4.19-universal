#!/bin/bash
LOG="$HOME/kernel-oc/build-$(date +%Y%m%d-%H%M).log"
echo "$LOG" > "$HOME/kernel-oc/build-latest.txt"
"$HOME/kernel-oc/tools/build_sashimi.sh" > "$LOG" 2>&1
echo "EXIT=$?" >> "$LOG"
