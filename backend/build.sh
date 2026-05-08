#!/usr/bin/env bash
set -o errexit

echo "Python version: $(python --version)"
pip install --upgrade pip
pip install -r requirements.txt
