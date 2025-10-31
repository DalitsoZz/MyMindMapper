#!/bin/sh
# Script used as GIT_EDITOR to supply the new commit message when rewording.
MSG_FILE="$1"

echo "initial import" > "$MSG_FILE"
exit 0
