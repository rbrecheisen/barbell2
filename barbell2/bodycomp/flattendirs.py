import argparse
import os
import shutil


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help='Input directory', default='.')
    parser.add_argument('--output_dir', help='Output directory', default='output')
    args = parser.parse_args()
    os.makedirs(args.output_dir)
    for root, dirs, files in os.walk(args.input_dir):
        for f_name in files:
            f_path = os.path.join(root, f_name)
            # Remove common root directory of each file's path
            f_name_new = f_path.replace(args.input_dir, '')[1:]
            # Replace slashes by underscores to build a new file name that's always unique
            f_name_new = f_name_new.replace(os.path.sep, '_')
            shutil.copy(f_path, os.path.join(args.output_dir, f_name_new))
            print(f_name_new)


if __name__ == '__main__':
    from barbell2 import common
    common.setup_args_env([
        '--input_dir=/Users/Ralph/data/surfdrive/projects/hpb/bodycomposition/data/l3tag_cohorts',
        '--output_dir=/Users/Ralph/Desktop/output',
    ])
    main()
