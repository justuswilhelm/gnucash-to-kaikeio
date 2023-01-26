#!/bin/sh
set -e
pipenv run isort .
pipenv run black .
