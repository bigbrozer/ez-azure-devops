#!/bin/bash

set -eu

next_version="$(git cliff --bumped-version)"

# Checks
if [[ -n $(git status --porcelain) ]]
then
  echo "Repo is dirty. Commit all changes first !"
  exit 1
fi

# Bump all versions
sed -r -i \
    "s/__version__ =.+/__version__ = \"${next_version:1}\"/" \
    src/ez_ados/version.py

# Prepare new changelog
git cliff --bump --output CHANGELOG.md
git add -A
git commit -m "chore(release): prepare for ${next_version}"
