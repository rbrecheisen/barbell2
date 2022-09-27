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
        '--mandatory_values', help='Values attributes must have', default='Rows=512,Columns=512')
    args = parser.parse_args()
    mandatory_attributes = [x.strip() for x in args.mandatory_attributes.split(',')]
    mandatory_values = [x.strip() for x in args.mandatory_values.split(',')]
    mandatory_values_dict = {}
    for value in mandatory_values:
        items = [x.strip() for x in value.split('=')]
        mandatory_values_dict[items[0]] = items[1]
    os.makedirs(args.output_dir)
    os.makedirs(args.output_dir_error)
    files_ok = []
    files_error = []
    for f in os.listdir(args.input_dir):
        f_path = os.path.join(args.input_dir, f)
        try:
            error = False
            p = pydicom.dcmread(f_path, stop_before_pixels=True)
            for attribute in mandatory_attributes:
                if attribute not in p:
                    error = True
                    files_error.append(f_path)
                    print(f'Attribute {attribute} not in {f_path}')
            for k, v in mandatory_values_dict.items():
                v_p = str(p[k].value)
                if v_p != v:
                    error = True
                    files_error.append(f_path)
                    print(f'Value {v_p} of {k} should be {v}')
            if not error:
                files_ok.append(f_path)
        except pydicom.errors.InvalidDicomError:
            pass
    for f in files_ok:
        shutil.copy(f, os.path.join(args.output_dir, os.path.split(f)[1]))
    for f in files_error:
        shutil.copy(f, os.path.join(args.output_dir_error, os.path.split(f)[1]))


if __name__ == '__main__':
    from barbell2 import common
    common.setup_args_env([
        '--input_dir=/Users/Ralph/data/surfdrive/projects/hpb/bodycomposition/data/l3tag_cohorts/SURG-PANC',
        '--output_dir=/Users/Ralph/Desktop/output',
        '--output_dir_error=/Users/Ralph/Desktop/error',
    ])
    main()
