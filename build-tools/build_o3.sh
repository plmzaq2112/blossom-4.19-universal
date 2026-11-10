#!/bin/bash
export EXTRA_KCFLAGS="-O3 -mcpu=cortex-a53+crc+crypto -fno-semantic-interposition"
exec "$HOME/kernel-oc/tools/run_build.sh"
