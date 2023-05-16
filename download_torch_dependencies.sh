#!/bin/bash

TORCHWHEELS_DIR=.torchwheels

mkdir -p $TORCHWHEELS_DIR

wget -P $TORCHWHEELS_DIR https://download.pytorch.org/whl/cu118/torch-2.0.1%2Bcu118-cp310-cp310-linux_x86_64.whl
wget -P $TORCHWHEELS_DIR https://download.pytorch.org/whl/cu118/torchvision-0.15.2%2Bcu118-cp310-cp310-linux_x86_64.whl