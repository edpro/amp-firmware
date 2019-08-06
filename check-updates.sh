#!/usr/bin/bash
set -e

C_WARN='\033[33m'
C_END='\033[0m'

cur_date=$(date +%Y-%m-%d)
#prev_date=$(cat .date || true)

if [ "$cur_date" == "$prev_date" ]; then
    exit 0
fi

echo "checking for updates..."
(git remote update || true) > /dev/null

LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @\{u\})
BASE=$(git merge-base @ @\{u\})

# echo "local: $LOCAL"
# echo "remote: $REMOTE"
# echo "base: $BASE"

if [ "$LOCAL" = "$REMOTE" ]; then
    echo -e "up-to-date"
elif [ "$LOCAL" = "$BASE" ]; then
    read -p "${C_WARN}Updates are available, update now? (y/n):'${C_END}"
    case $REPLY in
        [Yy]* ) echo "git pull";;
    esac

elif [ "$REMOTE" = "$BASE" ]; then
    echo -e "${C_WARN}Need to push${C_END}"
else
    echo -e "${C_WARN}Repository is not synchronized${C_END}"
fi

echo "$cur_date" > .date
