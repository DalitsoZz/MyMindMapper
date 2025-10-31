#!/bin/sh
# Helper script for git filter-branch --commit-filter
# Replaces the commit message for a specific commit SHA with a neutral message.

TARGET_SHA="d8dd5470ab0bb3032e183e3f07b353df5077f40b"
NEW_MSG="initial import"

if [ "$GIT_COMMIT" = "$TARGET_SHA" ]; then
  git commit-tree "$@" -m "$NEW_MSG"
else
  git commit-tree "$@"
fi
