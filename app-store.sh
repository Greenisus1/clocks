#!/bin/bash
# pi-app-store: 1
# pi-app-store-category: tools
# pi-app-store-description: World clock, countdown timer and stopwatch in one terminal app. Eleven time zones, pauseable timer with alarm, stopwatch with laps. Fully offline.
set -eu
cd -- "$(dirname -- "$0")"
case "${1:-}" in
 install) python3 -c 'from pathlib import Path;[compile(p.read_bytes(),str(p),"exec") for p in Path(".").glob("*.py")]' ;;
 run) shift; exec python3 clocks.py "$@" ;;
 *) echo 'Use: bash app-store.sh install OR bash app-store.sh run';exit 1 ;;
esac
