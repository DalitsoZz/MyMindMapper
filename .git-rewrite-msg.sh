
TARGET_SHA="d8dd5470ab0bb3032e183e3f07b353df5077f40b"
NEW_MSG="initial import"

if [ "$GIT_COMMIT" = "$TARGET_SHA" ]; then
  git commit-tree "$@" -m "$NEW_MSG"
else
  git commit-tree "$@"
fi
