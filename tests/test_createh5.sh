#!/usr/bin/env bash
export PYTHONPATH=${HOME}/dev/barbell2:${PYTHONPATH}

cd ../barbell2/createh5

python createh5.py \
    /Volumes/USB_SECURE1/data/radiomics/projects/deepseg/data/mega/final \
    ${HOME}/Desktop/h5 \
    --split="HEERLEN, NEWEPOC" \
    --split_percentage=0.8
