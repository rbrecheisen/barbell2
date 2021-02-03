import os
import pydicom

from barbell2.utils import Logger
from barbell2.lib.dicom import is_dicom, is_tag


class CreateHDF5:

    def __init__(self, dir_path, output_file, rows, columns, has_labels=True, split_percentage=1.0, log_dir='.'):

        self.dir_path = dir_path
        self.output_file = output_file
        self.rows = rows
        self.columns = columns
        self.split_percentage = split_percentage
        self.log = Logger(file_name_prefix='createh5_', to_dir=log_dir)
        self.has_labels = has_labels
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

    def collect_files(self, dir_path, rows, columns, has_labels):
        """
        Collect DICOM files and, if available, corresponding TAG files. Just put them in a flat list.
        Later we will figure out if there are TAG files to consider and whether these have the right
        dimension and labels.
        """
        files_list = []
        for root, dirs, files in os.walk(dir_path):
            for f in files:
                f = os.path.join(root, f)
                if is_dicom(f):
                    if self.has_dimensions(f, rows, columns):
                        if has_labels:
                            tag_file = self.get_tag_file_path(f)
                            if os.path.isfile(tag_file):
                                files_list.append(f)
                                files_list.append(tag_file)
                            else:
                                tag_file = self.get_tag_file_path(f, append=True)
                                if os.path.isfile(tag_file):
                                    files_list.append(f)
                                    files_list.append(tag_file)
                                else:
                                    self.log.print('File {} does not have TAG file'.format(f))
                        else:
                            pass
                    else:
                        self.log.print('File {} has wrong dimensions'.format(f))
                else:
                    pass
        return files_list

    @staticmethod
    def shuffle_files(files):
        return files

    @staticmethod
    def split_files(files, split_percentage):
        return files

    def create_hdf5(self):

        # TODO: figure out beforehand whether we have TAG files or not
        # TODO:
        # Build collection of file pairs where
        #  - Each L3 image has a corresponding TAG file
        #  - Each L3 image has the correct dimensions (rows x columns)
        #  - Each L3 image has pixels
        #  - Each L3 image has true HU pixel values
        # If TAG file present:
        #  - Each TAG file has pixels
        #  - Each TAG file has correct dimensions (and same dimensions as L3 image)
        #  - Each TAG file has correct labels (and only the correct labels)
        files = self.collect_files(self.dir_path, self.rows, self.columns)
        files = self.shuffle_files(files)
        training_files, validation_files = self.split_files(files, self.split_percentage)
