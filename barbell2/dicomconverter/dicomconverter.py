import os
import sys
import argparse

from barbell2.utils import MyException


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('source_dir', help='Source directory containing DICOM files to be converted')
    parser.add_argument('target_dir', help='Target directory where converted DICOM files will be copied to')
    args = parser.parse_args()
    return args


def run():

    # Get command-line arguments
    args = get_args()

    # Check that the gdcmconv tool exists
    result = os.system('which gdcmconv>/dev/null')
    if result > 0:
        raise MyException('Tool "gdcmconv" is probably not installed')

    # Check that source directory exists and is not empty. The target directory is not allowed to exist
    if not os.path.isdir(args.source_dir):
        raise MyException('Source directory "{}" does not exist'.format(args.source_dir))
    if len(os.listdir(args.source_dir)) == 0:
        raise MyException('Source directory "{}" is empty'.format(args.source_dir))
    if os.path.isdir(args.target_dir):
        raise MyException('Target directory "{}" exists. Please delete it first!'.format(args.target_dir))
    os.makedirs(args.target_dir, exist_ok=False)

    # Process DICOM files
    for file_name in os.listdir(args.source_dir):
        file_source_path = os.path.join(args.source_dir, file_name)
        file_target_path = os.path.join(args.target_dir, file_name)
        command = 'gdcmconv --raw {} {}'.format(file_source_path, file_target_path)
        os.system(command)
        print(command)


def main():
    try:
        run()
    except MyException as e:
        print(e)


if __name__ == '__main__':
    main()
