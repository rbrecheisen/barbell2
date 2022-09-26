from barbell2 import common

import os


def main():
    parser = common.get_parser()
    args = parser.parse_args()
    if args.input_dir != args.output_dir and args.overwrite == 1:
        pass
    for f in os.listdir(args.input_dir):
        print(f)


main()
