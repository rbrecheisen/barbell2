import os
import shutil
import pydicom
import pydicom.errors
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help='Input directory', default='.')
    parser.add_argument('--output_dir', help='Output directory', default='output')
    parser.add_argument('--output_dir_error', help='Output directory for files blocked by filter', default='error')
    parser.add_argument(
        '--mandatory_attributes', help='Attributes that must be present',
        default='Rows,Columns,PixelSpacing,BitsStored,BitsAllocated,RescaleSlope,RescaleIntercept')
    parser.add_argument(
        '--mandatory_values', help='Values attributes must have', default='Rows=512,Columns=512,BitsStored=16')
    args = parser.parse_args()
    mandatory_attributes = [x.strip() for x in args.mandatory_attributes.split(',')]
    mandatory_values = [x.strip() for x in args.mandatory_values.split(',')]
    mandatory_values_dict = {}
    for value in mandatory_values:
        items = [x.strip() for x in value.split('=')]
        mandatory_values_dict[items[0]] = items[1]
    os.makedirs(args.output_dir)
    os.makedirs(args.output_dir_error)
    for f in os.listdir(args.input_dir):
        f_path = os.path.join(args.input_dir, f)
        try:
            p = pydicom.dcmread(f_path, stop_before_pixels=True)
            for attribute in mandatory_attributes:
                if attribute not in p:
                    pass
        except pydicom.errors.InvalidDicomError:
            pass


if __name__ == '__main__':
    from barbell2 import common
    common.setup_args_env([
        '--input_dir=/Users/Ralph/data/surfdrive/projects/hpb/bodycomposition/data/l3tag_cohorts/SURG-PANC',
        '--output_dir=/Users/Ralph/Desktop/output',
    ])
    main()
