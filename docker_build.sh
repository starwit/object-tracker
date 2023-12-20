#!/bin/bash

if [ -z "$GITHUB_USER" ]; then
    read -p "GITHUB_USER: " GITHUB_USER
fi
if [ -z "$GITHUB_TOKEN" ]; then
    read -s -p "GITHUB_TOKEN: " GITHUB_TOKEN
fi

export GIT_CREDENTIALS="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com"

docker build --secret id=GIT_CREDENTIALS -t starwitorg/sae-object-tracker:$(poetry version --short) .