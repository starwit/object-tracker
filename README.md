# Object Tracker
This component is part of the Starwit Awareness Engine (SAE). See umbrella repo here: https://github.com/starwit/starwit-awareness-engine.

This component hooks into SAE's streams of frames annotated with detected objects and tracks them over multiple frames. This way for every detected object, a trajectory over time and pixel space is created.

## How to set up
- Make sure you have Poetry installed (otherwise see here: https://python-poetry.org/docs/#installing-with-the-official-installer)
- Set environment variable `NVIDIA_TENSORRT_DISABLE_INTERNAL_PIP=True` (otherwise `tensorrt-*` installation will fail)
- Run `poetry install`

## How to Build

See [dev readme](doc/DEV_README.md) for build & package instructions.

## Acknowledgements
This component is heavily influenced by [Mikel Brostrom's](https://github.com/mikel-brostrom/boxmot) fantastic library. Make sure to leave a star!