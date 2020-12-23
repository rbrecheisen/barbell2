import os
import argparse
import h5py
import sys
import pydicom

from barbell2.lib.dicom import Dcm2Numpy, Tag2NumPy


class MyException(Exception):
    pass


def info_requested(args):
    if len(args) == 2 and args[1] == '--info':
        return True
    return False


def show_info():
    print("""The createh5.py script allows you to create HDF5 files for training, validation and testing your
    deep learning networks in Keras.""")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('root_dir',
                        help='Root folder containing collection folders')
    parser.add_argument('output_dir',
                        help='Output folder where train.h5, validation.h5 and test.h5 will be written')
    parser.add_argument('--output_file_name_training',
                        help='Output file name training set', default='training.h5')
    parser.add_argument('--output_file_name_validation',
                        help='Output file name validation set', default='validation.h5')
    parser.add_argument('--output_file_name_testing',
                        help='Output file name test set', default='testing.h5')
    parser.add_argument('--height', type=int,
                        help='Image height in pixels (rows in DICOM header)', default=512)
    parser.add_argument('--width', type=int,
                        help='Image width in pixels (columns in DICOM header)', default=512)
    parser.add_argument('--training',
                        help='Comma-separated list of collection names for training')
    parser.add_argument('--validation',
                        help='Comma-separated list of collection names for validation')
    parser.add_argument('--testing',
                        help='Comma-separated list of collection names for validation')
    # https://stackoverflow.com/questions/8259001/python-argparse-command-line-flags-without-arguments
    # parser.add_argument('--info', help='Shows detailed help info', action='store_true')
    args = parser.parse_args()
    return args


def check_collections(root_dir, collections):
    collection_list = [x.strip() for x in collections.split(',')]
    for collection in collection_list:
        if not os.path.isdir(os.path.join(root_dir, collection)):
            raise MyException('Collection directory "{}" does not exist'.format(collection))
    print('Done')


def has_correct_dimensions(dcm_file, width, height):
    p = pydicom.read_file(dcm_file)
    if int(p.Rows) == height and int(p.Columns) == width:
        return True
    return False


def create_h5(root_dir, collections, width, height, output_file_path):
    file_list = []
    collection_list = [x.strip() for x in collections.split(',')]
    print(collection_list)
    for collection in collection_list:
        collection_dir = os.path.join(root_dir, collection)
        for root, dirs, files in os.walk(collection_dir):
            for f in files:
                if f.endswith('.dcm') and not f.startswith('._'):
                    dcm_file = os.path.join(root, f)
                    # Only allow images to be included that have the correct dimension (e.g., 512x512)
                    if has_correct_dimensions(dcm_file, width, height):
                        tag_file = os.path.join(root, f)[:-4] + '.tag'
                        if os.path.isfile(tag_file):
                            file_list.append([dcm_file, tag_file])
                            print('Adding {} to collection'.format(dcm_file))
    print('Creating H5...')
    with h5py.File(output_file_path, 'w') as h5f:
        count = 1
        for file_pair in file_list:
            dcm_pixels = get_dcm_pixels(file_pair[0])
            tag_pixels = get_tag_pixels(file_pair[1], dcm_pixels.shape)
            group = h5f.create_group('{:04d}'.format(count))
            group.create_dataset('images', data=dcm_pixels)
            group.create_dataset('labels', data=tag_pixels)
            print('{:04d} added images and labels for {}'.format(count, file_pair[0]))
            count += 1
    print('Done')


def get_dcm_pixels(file_path):
    dcm2numpy = Dcm2Numpy()
    dcm2numpy.set_input_dicom_file_path(file_path)
    dcm2numpy.execute()
    return dcm2numpy.get_output_numpy_array()


def get_tag_pixels(file_path, shape):
    tag2numpy = Tag2NumPy(shape)
    tag2numpy.set_input_tag_file_path(file_path)
    tag2numpy.execute()
    return tag2numpy.get_output_numpy_array()


def run():

    show_info()
    args = get_args()

    # Verify that root folder exists and is not empty
    if not os.path.isdir(args.root_dir):
        raise MyException('Root directory "{}" does not exist'.format(args.root_dir))
    if len(os.listdir(args.root_dir)) == 0:
        raise MyException('Root directory "{}" is empty'.format(args.root_dir))

    # Verify that output folder does not exist or delete it if so configured
    if os.path.isdir(args.output_dir):
        raise MyException(
            'Output directory "{}" exists. Please delete it'.format(args.output_dir))

    # Verify that training, validation and test collections exist and are not empty
    if args.training is not None:
        print('Checking collections training...')
        check_collections(args.root_dir, args.training)
    if args.validation is not None:
        check_collections(args.root_dir, args.validation)
    if args.testing is not None:
        check_collections(args.root_dir, args.testing)

    os.makedirs(args.output_dir, exist_ok=True)

    # Create training H5
    if args.training is not None:
        print('Creating H5 training...')
        create_h5(
            args.root_dir,
            args.training,
            args.width, args.height,
            os.path.join(args.output_dir, args.output_file_name_training))

    # Create validation H5
    if args.validation is not None:
        create_h5(
            args.root_dir,
            args.validation,
            args.width, args.height,
            os.path.join(args.output_dir, args.output_file_name_validation))

    # Create test H5
    if args.testing is not None:
        create_h5(
            args.root_dir,
            args.testing,
            args.width, args.height,
            os.path.join(args.output_dir, args.output_file_name_testing))


def main():
    try:
        run()
    except MyException as e:
        print(e)


if __name__ == '__main__':
    main()
