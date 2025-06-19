#!/bin/bash

# Check if settings.yaml exists
if [ ! -f "settings.yaml" ]; then
    echo "settings.yaml not found. Creating from template..."
    cp settings.template.yaml settings.yaml
    echo "settings.yaml created successfully."
else
    echo "settings.yaml already exists."
fi