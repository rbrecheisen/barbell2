from barbell2 import common


def main():
    parser = common.get_parser()
    print(parser.parse_args())
    # If output directory is same as input directory, decompressed files will be renamed to
    # original file name + _raw


main()
