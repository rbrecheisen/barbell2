import os
import argparse
import h5py
import pydicom
import random

import numpy as np

from barbell2.utils import MyException, Logger
from barbell2.lib.dicom import Dcm2Numpy, Tag2NumPy

from sklearn.model_selection import train_test_split

LOG = None


def info_requested(args):
    if len(args) == 2 and args[1] == '--info':
        return True
    return False


def show_intro():
    LOG.print("""
    === CREATEH5 ===
    Welcome to the createh5 tool of the Barbell2 package!
    This tool allows you to create HDF5 files from collections of single DICOM images and associated TAG files that
    contain segmentations of various regions of interest in the DICOM images. You can use the tool to create training,
    validation and test sets for deep learning with the Keras framework.
    """)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('root_dir', help='Root folder containing collection folders')
    parser.add_argument('output_dir', help='Output folder where train.h5, validation.h5 and test.h5 will be written')
    parser.add_argument('--output_file_name_training', help='Output file name training set', default='training.h5')
    parser.add_argument('--output_file_name_validation', help='Output file name validation set', default='validation.h5')
    parser.add_argument('--output_file_name_testing', help='Output file name test set', default='testing.h5')
    parser.add_argument('--height', type=int, help='Image height in pixels (rows in DICOM header)', default=512)
    parser.add_argument('--width', type=int, help='Image width in pixels (columns in DICOM header)', default=512)
    parser.add_argument('--training', help='Comma-separated list of collection names for training')
    parser.add_argument('--validation', help='Comma-separated list of collection names for validation')
    parser.add_argument('--testing', help='Comma-separated list of collection names for validation')
    parser.add_argument('--split', help='Comma-separated list of collection names for a 80/20 split between training and validation')
    parser.add_argument('--split_percentage', type=float, help='Percentage to split on (default: .8)', default=0.8)
    # https://stackoverflow.com/questions/8259001/python-argparse-command-line-flags-without-arguments
    # parser.add_argument('--info', help='Shows detailed help info', action='store_true')
    args = parser.parse_args()
    return args


def check_collections(root_dir, collections):
    collection_list = [x.strip() for x in collections.split(',')]
    for collection in collection_list:
        if not os.path.isdir(os.path.join(root_dir, collection)):
            raise MyException('Collection directory "{}" does not exist'.format(collection))
    LOG.print('Done')


def has_correct_dimensions(dcm_file, width, height):
    p = pydicom.read_file(dcm_file)
    if int(p.Rows) == height and int(p.Columns) == width:
        return True
    return False


def collect_files(root_dir, collections, width, height):
    file_list = []
    collection_list = [x.strip() for x in collections.split(',')]
    LOG.print(collection_list)
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
                            LOG.print('Adding {} to collection'.format(dcm_file))
    return file_list


def shuffle_file_list(file_list):
    random.shuffle(file_list)
    return file_list


def split_file_list(file_list, percentage):
    x_train, x_test = train_test_split(file_list, test_size=1.0 - percentage)
    return x_train, x_test


def get_dcm_pixels(file_path):
    dcm2numpy = Dcm2Numpy()
    dcm2numpy.set_input_dicom_file_path(file_path)
    dcm2numpy.set_normalize_enabled()
    dcm2numpy.execute()
    return dcm2numpy.get_output_numpy_array()


def get_tag_pixels(file_path, shape):
    tag2numpy = Tag2NumPy(shape)
    tag2numpy.set_input_tag_file_path(file_path)
    tag2numpy.execute()
    pixels = tag2numpy.get_output_numpy_array()
    # Note that sometimes pixels = None because of failure to reshape the pixel array
    # to the size of the DICOM image
    return pixels


def update_labels(pixels):
    # Alberta protocol: AIR = 0, MUSCLE = 1, IMAT = 2, VAT = 5, SAT = 7
    # pixels[pixels == 0] = 0
    pixels[pixels == 2] = 0
    pixels[pixels == 4] = 0
    pixels[pixels == 11] = 0
    pixels[pixels == 12] = 0
    pixels[pixels == 14] = 0
    # pixels[pixels == 1] = 1
    pixels[pixels == 5] = 2
    pixels[pixels == 7] = 3
    return pixels


def labels_ok(labels):
    for label in [0, 1, 2, 3]:
        if label not in labels:
            return False
    return len(labels) == 4


def update_label_counts(label_counts, labels):
    for label in labels:
        if label not in label_counts.keys():
            label_counts[label] = 1
        else:
            label_counts[label] += 1
    return label_counts


def create_h5_from_file_list(file_list, output_file_path):
    label_counts = {}
    with h5py.File(output_file_path, 'w') as h5f:
        count = 1
        for file_pair in file_list:
            file_name = os.path.split(file_pair[0])[1][:-4]
            dcm_pixels = get_dcm_pixels(file_pair[0])
            tag_pixels = get_tag_pixels(file_pair[1], dcm_pixels.shape)
            if tag_pixels is None:
                LOG.print('ERROR: Could not retrieve pixels from {}'.format(file_pair[1]))
                continue
            tag_pixels = update_labels(tag_pixels)
            labels = np.unique(tag_pixels)
            if not labels_ok(labels):
                LOG.print('ERROR: Labels not ok ({})'.format(labels))
                continue
            label_counts = update_label_counts(label_counts, labels)
            group = h5f.create_group('{}'.format(file_name))
            group.create_dataset('images', data=dcm_pixels)
            group.create_dataset('labels', data=tag_pixels)
            LOG.print('{:04d} added images and labels ({}) for patient {}'.format(count, labels, file_name))
            count += 1
    LOG.print('Done')
    LOG.print('{}: {}'.format(output_file_path, label_counts))


def run(args):

    # Verify that root folder exists and is not empty
    if not os.path.isdir(args.root_dir):
        raise MyException('Root directory "{}" does not exist'.format(args.root_dir))
    if len(os.listdir(args.root_dir)) == 0:
        raise MyException('Root directory "{}" is empty'.format(args.root_dir))

    # Verify that training, validation and test collections exist and are not empty
    if args.training is not None:
        LOG.print('Checking collections training...')
        check_collections(args.root_dir, args.training)
    if args.validation is not None:
        check_collections(args.root_dir, args.validation)
    if args.testing is not None:
        check_collections(args.root_dir, args.testing)
    if args.split is not None:
        check_collections(args.root_dir, args.split)
        if args.split_percentage is None:
            raise MyException('Argument --split_percentage is mandatory when choosing --split')

    # Create training H5
    if args.training is not None:
        file_list = collect_files(
            args.root_dir, args.training, args.width, args.height)
        file_list = shuffle_file_list(file_list)
        create_h5_from_file_list(
            file_list,
            os.path.join(args.output_dir, args.output_file_name_training))

    # Create validation H5
    if args.validation is not None:
        file_list = collect_files(
            args.root_dir, args.validation, args.width, args.height)
        file_list = shuffle_file_list(file_list)
        create_h5_from_file_list(
            file_list,
            os.path.join(args.output_dir, args.output_file_name_validation))

    # Create test H5
    if args.testing is not None:
        file_list = collect_files(
            args.root_dir, args.testing, args.width, args.height)
        file_list = shuffle_file_list(file_list)
        create_h5_from_file_list(
            file_list,
            os.path.join(args.output_dir, args.output_file_name_testing))

    # Create percentage split training/validation. Note that the split is done
    # across all collections, so everything is considered to be one big data set
    # that is split into parts.
    # Note: the args.split_percentage refers to the percentage of observations
    # assigned to the training set!
    if args.split is not None:
        file_list = collect_files(args.root_dir, args.split, args.width, args.height)
        file_list = shuffle_file_list(file_list)
        training_files, validation_files = split_file_list(file_list, args.split_percentage)
        LOG.print('>>> Creating training.h5...')
        create_h5_from_file_list(training_files, os.path.join(args.output_dir, args.output_file_name_training))
        LOG.print('>>> Creating validation.h5...')
        create_h5_from_file_list(validation_files, os.path.join(args.output_dir, args.output_file_name_validation))


def main():
    global LOG
    args = get_args()
    os.makedirs(args.output_dir, exist_ok=False)
    LOG = Logger(args.output_dir)
    show_intro()
    try:
        run(args)
    except MyException as e:
        LOG.print(e)


if __name__ == '__main__':
    main()
