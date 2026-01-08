#!/bin/bash
set -e

ruff check .

python -m unittest discover test
