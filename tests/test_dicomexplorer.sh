#!/usr/bin/env bash
export PYTHONPATH=${HOME}/dev/barbell2:${PYTHONPATH}

cd ../barbell2/dicomexplorer

python dicomexplorer.py

# TODO: how to test this?
