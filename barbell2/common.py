import sys
import argparse


def setup_args_env(arg_list):
    for arg in arg_list:
        sys.argv.append(arg)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', help='Input directory', default='.')
    parser.add_argument('--output-dir', help='Output directory', default='output')
    parser.add_argument('--overwrite', help='Whether to overwrite output', type=int, default=1)
    return parser
