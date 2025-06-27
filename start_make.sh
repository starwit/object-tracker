#!/bin/bash

# Purpose of this script is to enforce a bash environment when calling make
export PACKAGE_NAME=objectdetector

export PATH=/root/.local/bin/:$PATH
cd /code

make build-deb

