#!/bin/bash

docker build -t starwitorg/sae-object-tracker:$(poetry version --short) .