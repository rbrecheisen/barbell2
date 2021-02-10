import os
import h5py
import random
import pydicom
import numpy as np

from barbell2.utils import Logger
from barbell2.lib.dicom import is_dicom
from barbell2.lib.dicom import Dcm2Numpy, Tag2NumPy

from sklearn.model_selection import train_test_split


class CreateHDF5:

    def __init__(self, dir_path, output_files, rows, columns, test_size=0.0, is_training=True, log_dir='.'):
        self.dir_path = dir_path
        self.is_training = is_training
        if isinstance(output_files, str):
            self.output_files = [output_files]
        else:
            self.output_files = output_files
        if not self.is_training:
            if len(self.output_files) != 1:
                raise RuntimeError('For prediction provide only one output file')
        self.rows = rows
        self.columns = columns
        self.test_size = test_size
        os.makedirs(log_dir, exist_ok=True)
        self.log = Logger(prefix='createh5_', to_dir=log_dir)

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

    def collect_files(self, dir_path, rows, columns, is_training):
        files_list = []
        count = 1
        for root, dirs, files in os.walk(dir_path):
            for f in files:
                f = os.path.join(root, f)
                if is_dicom(f):
                    if self.has_dimensions(f, rows, columns):
                        if is_training:
                            append = False
                            tag_file = self.get_tag_file_path(f)
                            if os.path.isfile(tag_file):
                                append = True
                            else:
                                tag_file = self.get_tag_file_path(f, append=True)
                                if os.path.isfile(tag_file):
                                    append = True
                                else:
                                    self.log.print('File {} does not have TAG file'.format(f))
                            if append:
                                files_list.append((f, tag_file))
                                self.log.print('{:03d} Appended {} and TAG file'.format(count, f))
                                count += 1
                        else:
                            files_list.append((f, ))
                            self.log.print('{:03d} Appended {}'.format(count, f))
                            count += 1
                    else:
                        self.log.print('File {} has wrong dimensions'.format(f))
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

    def create_file(self, output_file, files):
        with h5py.File(output_file, 'w') as h5f:
            count = 1
            for file_pair in files:
                file_id = self.get_file_id(file_pair[0])
                dcm_pixels = self.get_dcm_pixels(file_pair[0])
                if dcm_pixels is None:
                    self.log.print('DICOM file {} has problems with pixel data'.format(file_pair[0]))
                    continue
                if self.is_training:
                    tag_pixels = self.get_tag_pixels(file_pair[1], dcm_pixels.shape)
                    if tag_pixels is None:
                        self.log.print('TAG file {} cannot be reshaped to right dimensions'.format(file_pair[1]))
                        continue
                    tag_pixels, unique_labels = self.update_labels(tag_pixels)
                    if tag_pixels is None:
                        self.log.print('TAG file {} has wrong labels {}'.format(file_pair[1], unique_labels))
                        continue
                    group = h5f.create_group('{}'.format(file_id))
                    group.create_dataset('image', data=dcm_pixels)
                    group.create_dataset('labels', data=tag_pixels)
                    self.log.print('{:04d} added images and labels for file ID {}'.format(count, file_id))
                    count += 1
                else:
                    group = h5f.create_group('{}'.format(file_id))
                    group.create_dataset('images', data=dcm_pixels)
            self.log.print('Done')

    def create_hdf5(self):
        if self.is_training:
            self.log.print('Collecting files for training')
        else:
            self.log.print('Collecting files for prediction')
        files = self.collect_files(self.dir_path, self.rows, self.columns, self.is_training)
        if self.is_training and self.test_size > 0.0:
            self.log.print('Shuffling files before training/test split')
            files = self.shuffle_files(files)
        if self.test_size < 1.0:
            self.log.print('Splitting files with test size of {}%'.format(int(100 * self.test_size)))
        training_files, test_files = self.split_files(files, self.test_size)
        self.log.print('Training files: {}'.format(len(training_files)))
        self.log.print('Test files: {}'.format(len(test_files)))
        self.log.print('Creating H5 training file')
        self.create_file(self.output_files[0], training_files)
        if len(self.output_files) == 2:
            self.log.print('Creating H5 test file')
            self.create_file(self.output_files[1], test_files)
            return self.output_files[0], self.output_files[1]
        else:
            return self.output_files[0], None
