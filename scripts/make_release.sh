#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

VERSION=$1

echo $VERSION

if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
	echo ERROR: Wrong version format \"$VERSION\". X.Y.Z expcted.
	exit -1
fi

if [[ `git status -s | wc -l` -ne 0 ]]; then
	echo ERROR: Git repository has uncommited changes. Please commit \& push them or stash them before preceeding.
	# exit -2
fi

if [[ `git branch --show-current` != "master" ]]; then
	echo ERROR: Current branch is not master, please checkout master
	exit -3
fi

echo "Bumping VERSION.txt to $VERSION"
echo $VERSION > $SCRIPT_DIR/../VERSION.txt

echo "Creating RELEASE commit for version $VERSION"
git add ..
git commit -m "RELEASE of version $VERRSION"

VERSION_TAG=v$VERSION
echo "Creating tag \"$VERSION_TAG\""
git tag $VERSION_TAG

echo "Pushing master branch and tag to origin"
# git push origin master $VERSION_TAG
