import os
import h5py
import random
import pydicom
import argparse
import numpy as np

from types import SimpleNamespace

from barbell2.utils import Logger
from barbell2.lib.dicom import is_dicom
from barbell2.lib.dicom import Dcm2Numpy, Tag2NumPy

from sklearn.model_selection import train_test_split


class CreateH5:

    def __init__(self, args):
        if isinstance(args, dict):
            self.args = SimpleNamespace(**args)
        else:
            self.args = args
        self.logger = Logger(
            prefix='createh5', to_dir=self.args.log_dir)

    @staticmethod
    def has_dimensions(dcm_file, rows, columns):
        p = pydicom.read_file(dcm_file)
        if int(p.Rows) == rows and int(p.Columns) == columns:
            return True
        return False

    @staticmethod
    def get_tag_file_path(dcm_file, append=False):
        if dcm_file.endswith('.dcm') and not append:
            return dcm_file[:-4] + '.tag'
        else:
            return dcm_file + '.tag'

    def collect_files(self, data_dir, rows, columns, is_train):
        count = 1
        files_list = []
        for root, dirs, files in os.walk(data_dir):
            for f in files:
                f = os.path.join(root, f)
                if is_dicom(f):
                    if self.has_dimensions(f, rows, columns):
                        if is_train:
                            # Try to get the TAG file path. If we can't find it, try not
                            # replacing the 'dcm' extension with '.tag' but simply append to it
                            ok = False
                            tag_file = self.get_tag_file_path(f)
                            if os.path.isfile(tag_file):
                                ok = True
                            else:
                                tag_file = self.get_tag_file_path(f, append=True)
                                if os.path.isfile(tag_file):
                                    ok = True
                            if ok:
                                files_list.append((f, tag_file))
                                self.logger.print('{:03d} Added {} and TAG file'.format(count, f))
                                count += 1
                            else:
                                self.logger.print('File {} does not have corresponding TAG file'.format(f))
                        else:
                            files_list.append((f, ))
                            self.logger.print('{:03d} Added {}'.format(count, f))
                    else:
                        self.logger.print('File {} has wrong dimensions'.format(f))
                else:
                    pass
        return files_list

    @staticmethod
    def shuffle_files(files):
        random.shuffle(files)
        return files

    @staticmethod
    def split_files(files, test_size):
        if test_size > 0.0:
            return train_test_split(files, test_size=test_size)
        return files, []

    @staticmethod
    def get_dcm_pixels(file_path):
        dcm2numpy = Dcm2Numpy()
        dcm2numpy.set_input_dicom_file_path(file_path)
        dcm2numpy.set_normalize_enabled()  # To ensure true HU values
        dcm2numpy.execute()
        return dcm2numpy.get_output_numpy_array()

    @staticmethod
    def get_tag_pixels(file_path, shape):
        tag2numpy = Tag2NumPy(shape)
        tag2numpy.set_input_tag_file_path(file_path)
        tag2numpy.execute()
        pixels = tag2numpy.get_output_numpy_array()
        # Note that sometimes pixels = None because of failure to reshape the pixel array
        # to the size of the DICOM image
        return pixels

    @staticmethod
    def labels_ok(labels):
        for label in [0, 1, 2, 3]:
            if label not in labels:
                return False
        return len(labels) == 4

    def update_labels(self, pixels):
        pixels[pixels == 2] = 0
        pixels[pixels == 4] = 0
        pixels[pixels == 11] = 0
        pixels[pixels == 12] = 0
        pixels[pixels == 14] = 0
        pixels[pixels == 5] = 2
        pixels[pixels == 7] = 3
        labels = np.unique(pixels)
        if self.labels_ok(labels):
            return pixels, labels
        return None, None

    @staticmethod
    def get_file_id(file_path):
        items = os.path.split(file_path)
        file_id = os.path.splitext(items[1])[0]
        return file_id

    def create_file(self, files, output_file, is_train):
        with h5py.File(output_file, 'w') as h5f:
            count = 1
            for file_pair in files:
                file_id = self.get_file_id(file_pair[0])
                dcm_pixels = self.get_dcm_pixels(file_pair[0])
                if dcm_pixels is None:
                    self.logger.print('DICOM file {} has problems with pixel data'.format(file_pair[0]))
                    continue
                if is_train:
                    tag_pixels = self.get_tag_pixels(file_pair[1], dcm_pixels.shape)
                    if tag_pixels is None:
                        self.logger.print('TAG file {} cannot be reshaped to right dimensions'.format(file_pair[1]))
                        continue
                    tag_pixels, unique_labels = self.update_labels(tag_pixels)
                    if tag_pixels is None:
                        self.logger.print('TAG file {} has wrong labels {}'.format(file_pair[1], unique_labels))
                        continue
                    group = h5f.create_group('{}'.format(file_id))
                    group.create_dataset('image', data=dcm_pixels)
                    group.create_dataset('labels', data=tag_pixels)
                    self.logger.print('{:04d} added images and labels for file ID {}'.format(count, file_id))
                    count += 1
                else:
                    group = h5f.create_group('{}'.format(file_id))
                    group.create_dataset('images', data=dcm_pixels)

    def execute(self):
        is_train = True if self.args.type == 'train' else False
        if is_train:
            self.logger.print('Collecting files for training')
        else:
            self.logger.print('Collecting files for prediction')
        files_list = self.collect_files(
            self.args.data_dir, self.args.rows, self.args.columns, is_train)
        if is_train and self.args.test_size > 0.0:
            self.logger.print('Shuffling files before training/test split')
            files_list = self.shuffle_files(files_list)
        if is_train and self.args.test_size > 0.0:
            self.logger.print('Splitting files with test size of {}%'.format(int(100 * self.args.test_size)))
        training_files, test_files = self.split_files(files_list, self.args.test_size)
        self.logger.print('Training files: {}'.format(len(training_files)))
        if is_train and self.args.test_size > 0.0:
            self.logger.print('Test files: {}'.format(len(test_files)))
        if is_train and self.args.test_size > 0.0:
            self.logger.print('Creating H5 file for testing')
            self.create_file(test_files, 'test.h5', is_train)
        if is_train:
            self.logger.print('Creating H5 file for training')
            self.create_file(training_files, 'train.h5', is_train)
        else:
            self.logger.print('Creating H5 file for prediction')
            self.create_file(training_files, 'predict.h5', is_train)
        self.logger.print('Done')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'data_dir',
        help='Directory containing DICOM and (optionally) TAG files',
    )
    parser.add_argument(
        '--rows',
        help='Number of pixel rows in each image, same as image height (default: 512)',
        type=int, default=512,
    )
    parser.add_argument(
        '--columns',
        help='Number of pixel columns in each image, same as image width (default: 512)',
        type=int, default=512,
    )
    parser.add_argument(
        '--type',
        help='Which type of H5 file to create. One of [train, predict] (default: train)',
        default='train',
    )
    parser.add_argument(
        '--test_size',
        help='Percentage of data to use for testing (between 0 and 1, default: 0.2)',
        type=float, default=0.2,
    )
    parser.add_argument(
        '--log_dir',
        help='Directory where to write logging info (default: .)',
        default='.',
    )
    args = parser.parse_args()
    x = CreateH5(args)
    x.execute()


if __name__ == '__main__':
    main()
