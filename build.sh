#!/usr/bin/env bash

set -ex

pipenv run python3 build.py

git add .
