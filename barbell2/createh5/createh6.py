import os
import h5py
import random
import pydicom

from barbell2.utils import Logger
from barbell2.lib.dicom import is_dicom
from sklearn.model_selection import train_test_split


class CreateHDF5:

    def __init__(self, dir_path, output_files, rows, columns, split_percentage=1.0, is_training=True, log_dir='.'):

        self.dir_path = dir_path
        self.is_training = is_training
        if self.is_training:
            self.output_files = output_files
            if len(self.output_files) != 2:
                raise RuntimeError('For training provide two output files')
        else:
            self.output_files = [output_files]
            if len(self.output_files) != 1:
                raise RuntimeError('For prediction provide only one output file')
        self.rows = rows
        self.columns = columns
        self.split_percentage = split_percentage
        os.makedirs(log_dir, exist_ok=True)
        self.log = Logger(file_name_prefix='createh5_', to_dir=log_dir)
        self.labels = {
            'air': 0,
            'muscle': 1,
            'vat': 5,
            'sat': 7,
        }

    def set_label(self, name, value):
        # Alberta protocol:
        #  - air = 0
        #  - muscle = 1
        #  - inter-muscular adipose tissue = 2 (IMAT)
        #  - visceral fat = 5 (VAT)
        #  - subcutaneous fat = 7 (SAT)
        self.labels[name] = value

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
        """
        Collect DICOM files and, if available, corresponding TAG files. Just put them in a flat list.
        Later we will figure out if there are TAG files to consider and whether these have the right
        dimension and labels.
        """
        if is_training:
            self.log.print('Collecting files for training')
        else:
            self.log.print('Collecting files for prediction')
        files_list = []
        count = 1
        # TODO: Make sure you store DICOM and TAG files as tuple pairs!
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

    def shuffle_files(self, files):
        self.log.print('Shuffling files before training/test split')
        random.shuffle(files)
        return files

    def split_files(self, files, percentage):
        if percentage < 1.0:
            self.log.print('Splitting files with test size of {}%'.format(int(100*(1.0-percentage))))
            return train_test_split(files, test_size=1.0 - percentage)
        return files, []

    def create_hdf5(self):
        self.log.print('Creating HDF5 file')

        # Build collection of file pairs where
        #  - Each L3 image has a corresponding TAG file
        #  - Each L3 image has the correct dimensions (rows x columns)
        #  - Each L3 image has pixels
        #  - Each L3 image has true HU pixel values
        # If TAG file present:
        #  - Each TAG file has pixels
        #  - Each TAG file has correct dimensions (and same dimensions as L3 image)
        #  - Each TAG file has correct labels (and only the correct labels)

        files = self.collect_files(self.dir_path, self.rows, self.columns, self.is_training)
        if self.is_training and self.split_percentage < 1.0:
            files = self.shuffle_files(files)
        training_files, test_files = self.split_files(files, self.split_percentage)
        self.log.print('Training files: {}'.format(len(training_files)))
        self.log.print('Test files: {}'.format(len(test_files)))

        # with h5py.File(self.output_files[0], 'w') as h5f:
        # INDENT
        for file_pair in training_files:
            dcm_pixels = get_dcm_pixels(file_pair[0])
            if self.is_training:
                tag_pixels = get_tag_pixels(file_pair[1])

        # INDENT
