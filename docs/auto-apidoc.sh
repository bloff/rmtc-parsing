#!/usr/bin/env bash

export PYTHON=python3

python docs/my-sphinx-apidoc.py -feE -o docs/API/ anoky

rm docs/API/anoky.rst
rm docs/API/modules.rst