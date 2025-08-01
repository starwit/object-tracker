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

## Github Workflows and Versioning

The following Github Actions are available:

* [PR build](.github/workflows/pr-build.yml): Builds python project for each pull request to main branch. `poetry install` and `poetry run pytest` are executed, to compile and test python code.
* [Build and publish latest image](.github/workflows/build-publish-latest.yml): Manually executed action. Same like PR build. Additionally puts latest docker image to internal docker registry.
* [Create release](.github/workflows/create-release.yml): Manually executed action. Creates a github release with tag, docker image in internal docker registry, helm chart in chartmuseum by using and incrementing the version in pyproject.toml. Poetry is updating to next version by using "patch, minor and major" keywords. If you want to change to non-incremental version, set version in directly in pyproject.toml and execute create release afterwards.

## Dependabot Version Update

With [dependabot.yml](.github/dependabot.yml) a scheduled version update via Dependabot is configured. Dependabot creates a pull request if newer versions are available and the compilation is checked via PR build.