#!/bin/sh
set -e
pipenv run flake8 .
pipenv run mypy
pipenv run python -m pytest
