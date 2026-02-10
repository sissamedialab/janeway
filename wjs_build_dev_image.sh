#!/bin/bash

set -e

if [[ -z "$2" ]]; then
    echo "Usage: $0 <tag> <branch>"
    exit 1
fi

number=$1
shift
branch=$1
shift

export TAG="registry.gitlab.sissamedialab.it/wjs/janeway/debian-python-git-janeway:${number}"
export CI_COMMIT_BRANCH=${branch}
docker build --tag $TAG --build-arg BUILDKIT_INLINE_CACHE=1 --build-arg BRANCH=$CI_COMMIT_BRANCH --file ./dockerfiles/Dockerfile.wjs ./dockerfiles
docker push ${TAG}