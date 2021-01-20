#!/usr/bin/env bash
export PYTHONPATH=${HOME}/dev/barbell2:${PYTHONPATH}

cd ../barbell2/createh5

python createh5.py \
    /Volumes/USB_SECURE1/data/radiomics/projects/deepseg/data/mega/final \
    ${HOME}/Desktop/h5 \
    --output_file_name_training=training.h5 \
    --output_file_name_validation=validation.h5 \
    --split="FROGS, HEERLEN, MAASTRICHT_AKEN, NEWEPOC" \
    --split_percentage=0.8

#python createh5.py \
#    --output_file_name_testing=testing.h5 \
#    --testing="TRAUMA" \
#    /Volumes/USB_SECURE1/data/radiomics/projects/deepseg/data/mega/final \
#    ${HOME}/Desktop/h5
