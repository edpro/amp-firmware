#!/usr/bin/bash
set -e
cd "$(dirname "$0")"
source ./env.sh

./check-updates.sh

python tools/ps_main.py