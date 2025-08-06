#!/bin/bash

docker build -t starwitorg/sae-object-tracker:$(git rev-parse --short HEAD) .