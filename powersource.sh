#!/usr/bin/bash
cd "$(dirname "$0")" || exit 1
source ./env.sh

./check-updates.sh

python tools/ps_main.py

if [[ "$?" != "0" ]]; then
  read -p "Error has occured..."
fi