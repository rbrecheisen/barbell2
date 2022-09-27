import os
import shutil
import pydicom
import pydicom.errors
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help='Input directory', default='.')
    parser.add_argument('--output_dir', help='Output directory', default='output')
    args = parser.parse_args()
    os.makedirs(args.output_dir)
    for f in os.listdir(args.input_dir):
        f_path = os.path.join(args.input_dir, f)
        try:
            pydicom.dcmread(f_path, stop_before_pixels=True)
            if not f.endswith('.dcm'):
                f_path_new = os.path.join(args.output_dir, f + '.dcm')
            else:
                f_path_new = os.path.join(args.output_dir, f)
            shutil.copy(f_path, f_path_new)
            print(f_path_new)
        except pydicom.errors.InvalidDicomError:
            pass


if __name__ == '__main__':
    from barbell2 import common
    common.setup_args_env([
        '--input_dir=/Users/Ralph/data/surfdrive/projects/hpb/bodycomposition/data/l3tag_cohorts/SURG-PANC',
        '--output_dir=/Users/Ralph/Desktop/output',
    ])
    main()
