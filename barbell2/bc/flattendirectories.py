from barbell2 import common

import os
import shutil


def main():
    parser = common.get_parser()
    args = parser.parse_args()
    if args.input_dir == args.output_dir:
        raise RuntimeError('Input and output directories cannot be the same')
    if args.overwrite == 1 and os.path.isdir(args.output_dir):
        shutil.rmtree(args.output_dir)
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


common.setup_args_env([
    '--input-dir=/Users/Ralph/data/surfdrive/projects/hpb/bodycomposition/data/l3tag_cohorts',
    '--output-dir=/Users/Ralph/Desktop/output',
    '--overwrite=1',
])
main()
