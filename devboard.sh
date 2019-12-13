#!/usr/bin/bash
cd "$(dirname "$0")" || exit 1

source ./env.sh

./update.sh

python tools/db_main.py || read -rp "Error has occured..."
