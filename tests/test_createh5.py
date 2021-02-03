import os

from barbell2 import CreateHDF5


def test_training_test():
    # Define output files
    d1 = '{}/data/surfdrive/projects/20210203_autosegl3/dicom_and_tag'.format(os.environ['HOME'])
    f1 = '{}/Desktop/training.h5'.format(os.environ['HOME'])
    f2 = '{}/Desktop/test.h5'.format(os.environ['HOME'])
    log_dir = '{}/Desktop/logs_training_test'.format(os.environ['HOME'])
    # Create HDF5 files
    m = CreateHDF5(d1, [f1, f2], 512, 512, 0.8, is_training=True, log_dir=log_dir)
    m.create_hdf5()


def test_training():
    # Define output files
    d1 = '{}/data/surfdrive/projects/20210203_autosegl3/dicom_and_tag'.format(os.environ['HOME'])
    f1 = '{}/Desktop/training.h5'.format(os.environ['HOME'])
    log_dir = '{}/Desktop/logs_training'.format(os.environ['HOME'])
    # Create HDF5 files
    m = CreateHDF5(d1, f1, 512, 512, is_training=True, log_dir=log_dir)
    m.create_hdf5()


def test_prediction():
    # Define output files
    d = '{}/data/surfdrive/projects/20210203_autosegl3/dicom'.format(os.environ['HOME'])
    f = '{}/Desktop/prediction.h5'.format(os.environ['HOME'])
    log_dir = '{}/Desktop/logs_prediction'.format(os.environ['HOME'])
    # Create HDF5 file
    m = CreateHDF5(d, f, 512, 512, is_training=False, log_dir=log_dir)
    m.create_hdf5()
