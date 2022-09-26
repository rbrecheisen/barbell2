import os
import shutil
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help='Input directory', default='.')
    parser.add_argument('--output_dir', help='Output directory', default='output')
    parser.add_argument('--extension', help='File extension to be copied', default='')
    args = parser.parse_args()
    os.makedirs(args.output_dir)
    for f in os.listdir(args.input_dir):
        if f.endswith(args.extension):
            f_path = os.path.join(args.input_dir, f)
            shutil.copy(f_path, args.output_dir)
            print(f_path)


if __name__ == '__main__':
    from barbell2 import common
    common.setup_args_env([
        '--input_dir=/Users/Ralph/data/surfdrive/projects/hpb/bodycomposition/data/l3tag_cohorts/SURG-PANC',
        '--output_dir=/Users/Ralph/Desktop/output',
        '--extension=tag',
    ])
    main()
