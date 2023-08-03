#!/bin/bash
# Bump a new release. Handling is the same as with poetry version,
# but also takes care of __init__.py:version, git tag, ...

if [[ -n "$(git status --porcelain | grep -v ' M WHATSNEW.md')" ]] ; then
  echo "error: git repository is not clean (except of WHATSNEW.md), please commit and/or stash all changes (except of WHATSNEW.md) before running this script."
  exit 1
fi

if [[ $# != 1 ]] ; then
  version_bump="not_implemented"
else
  version_bump=$1
fi

case $version_bump in
  major|minor|patch)
    ;;
  *)
    echo "ERROR: Please provide the version desired bump as 'major', 'minor' or 'patch'" >&2
    exit 1
esac

old_version=`poetry version | sed 's/fotoobo \(.*\)/\1/'`

poetry version $version_bump

new_version=`poetry version | sed 's/fotoobo \(.*\)/\1/'`

echo "New version would be $new_version. Is this ok? [y/N]"
read ok

case $ok in
  y)
    ;;
  *)
    echo "aborting..."
    git restore pyproject.toml
    exit 1
esac

echo 'Writing new version to "fotoobo/__init__.py"...'
sed -i "s/$old_version/$new_version/g" fotoobo/__init__.py

echo "Updating CHANGELOG.md"
sed -i -e '/./,$!d' -e :a -e '/^\n*$/{$d;N;ba' -e '}' WHATSNEW.md
VERSION="## [$new_version] - $(date +%Y-%m-%d)"
WHATSNEW="$(<WHATSNEW.md)"
sed -i "1s/^/\n$VERSION\n\n/" WHATSNEW.md
echo "" > WHATSNEW.md
sed -i '/# \[Released\]/r WHATSNEW.md' CHANGELOG.md


git add pyproject.toml
git add fotoobo/__init__.py
git add CHANGELOG.md
git add WHATSNEW.md

echo 'Committing version bump...'
git commit -m ":bookmark: Commit version v$new_version"
echo 'Pushing version bump...'
git push

echo "1st step done. Now create a pull request to the upstream repository and ask a maintainer to create the tag for you."
