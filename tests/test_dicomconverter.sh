#!/usr/bin/env bash

export PYTHONPATH=${HOME}/dev/barbell2:${PYTHONPATH}

cd ../barbell2/dicomconverter

python dicomconverter.py \
    $HOME/data/deepseg/leanne \
    $HOME/data/deepseg/leanne_unc
