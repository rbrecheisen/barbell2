import os
import argparse


def main():
    """
    Script that takes list of L3 images and runs Leroy's TF model on them to predict
    muscle and fat regions. 
    --file_list  List of file paths of DICOM images to process
    --output_dir Directory where to store output
    --model_file TensorFlow model file
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_list', help='List of DICOM files')
    parser.add_argument('--output_dir', help='Output directory', default='output')
    parser.add_argument('--model_file', help='TensorFlow model file')
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=False)
    for file_path in args.file_list:
        print(file_path)


if __name__ == '__main__':
    from barbell2 import common
    common.setup_args_env([
        '--input_dir=/Users/Ralph/data/surfdrive/projects/hpb/bodycomposition/data/l3tag_cohorts',
        '--output_dir=/Users/Ralph/Desktop/output',
    ])
    main()
