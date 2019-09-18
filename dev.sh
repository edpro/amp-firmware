#!/usr/bin/bash

cd "$(dirname "$0")" || exit 1

source ./env.sh

python ./tools/ui/menu.py

exit_code="$?"

if [[ "$exit_code" != "0" ]]; then
  read -p "Failed fith error code: $exit_code"
fi