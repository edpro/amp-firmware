#!/usr/bin/bash
set -e

cur_date=$(date +%Y-%m-%d)
prev_date=$(cat .date || true).

if [ "$cur_date" == "$prev_date" ]; then
    exit 0
fi

echo "checking for update..."
git remote update || true > /dev/null

LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})
BASE=$(git merge-base @ @{u})

# echo "local: $LOCAL"
# echo "remote: $REMOTE"
# echo "base: $BASE"

C_WARN='\033[33m'
C_ERR='\033[1;41m'
C_END='\033[0m'

if [ $LOCAL = $REMOTE ]; then
    echo -e "Up-to-date"
elif [ $LOCAL = $BASE ]; then
    echo -e "${C_WARN}-------------------------------------${C_END}"
    echo -e "${C_WARN}Updates are available! run 'git pull'${C_END}"
    echo -e "${C_WARN}-------------------------------------${C_END}"
elif [ $REMOTE = $BASE ]; then
    echo -e "${C_WARN}Need to push${C_END}"
else
    echo -e "${C_WARN}Repository is not synchronized${C_END}"
fi

echo $cur_date > .date
