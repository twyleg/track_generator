#!/bin/bash

VERSION=$1

echo $VERSION

if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
	echo ERROR: Wrong version format \"$VERSION\". X.Y.Z expcted.
	exit -1
fi

if [[ `git status -s | wc -l` -ne 0 ]]; then
	echo ERROR: Git repository has uncommited changes. Please commit \& push them or stash them before preceeding.
fi
