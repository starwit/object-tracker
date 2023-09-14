#!/bin/bash

docker push docker.internal.starwit-infra.de/sae/object-tracker:$(poetry version --short)