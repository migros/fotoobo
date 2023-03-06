#!/bin/bash
# Tag a new release, prepared by .make_release.sh .
# This needs to be run on the main repository.

new_version=`poetry version | sed 's/fotoobo \(.*\)/\1/'`

echo 'Create and push tag...'
git tag -a "v$new_version" -m "Version v$new_version"
git push origin "v$new_version"

echo "Done. Version $new_version is now released on GitHub (and soon on PyPi, etc.)."
echo -e "Congratulations \U2727"
