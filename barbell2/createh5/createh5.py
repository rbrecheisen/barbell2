import os
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('root_dir', help='Root folder containing collection folders')
parser.add_argument('output_dir', help='Output folder where files train.h5, validation.h5 and test.h5 will be written')
parser.add_argument('--training', help='Comma-separated list of collection names for training')
parser.add_argument('--validation', help='Comma-separated list of collection names for validation')
parser.add_argument('--test', help='Comma-separated list of collection names for validation')
args = parser.parse_args()


def check_collections(root_dir, collections):
    collection_list = [x.strip() for x in collections.split(',')]
    for collection in collection_list:
        if not os.path.isdir(os.path.join(root_dir, collection)):
            raise RuntimeError('Collection directory "{}" for does not exist'.format(collection))


def run():

    # Verify that root folder exists and is not empty
    if not os.path.isdir(args.root_dir):
        raise RuntimeError('Root directory "{}" does not exist'.format(args.root_dir))
    if len(os.listdir(args.root_dir)) == 0:
        raise RuntimeError('Root directory "{}" is empty'.format(args.root_dir))

    # Verify that output folder does not exist
    if os.path.isdir(args.output_dir):
        raise RuntimeError('Output directory "{}" exists. Please delete it'.format(args.output_dir))

    # Verify that training, validation and test collections exist and are not empty
    if args.training is not None:
        check_collections(args.root_dir, args.training)
    if args.validation is not None:
        check_collections(args.root_dir, args.validation)
    if args.test is not None:
        check_collections(args.root_dir, args.test)

    # Create training H5

    # Create validation H5

    # Create test H5


if __name__ == '__main__':
    run()
