import os

from barbell2 import CreateHDF5


def test_training():
    d1 = '/Users/Ralph/data/surfdrive/projects/20210203_autosegl3/dicom_and_tag'
    f1 = '/Users/Ralph/data/surfdrive/projects/20210203_autosegl3/training.h5'
    f2 = '/Users/Ralph/data/surfdrive/projects/20210203_autosegl3/test.h5'
    m = CreateHDF5(d1, [f1, f2], 512, 512, 0.8, is_training=True,
                   log_dir=os.path.join(os.environ['HOME'], 'Desktop', 'logs_train'))
    m.create_hdf5()


def test_prediction():

    d = '/Users/Ralph/data/surfdrive/projects/20210203_autosegl3/dicom'
    f = '/Users/Ralph/data/surfdrive/projects/20210203_autosegl3/prediction.h5'
    m = CreateHDF5(d, f, 512, 512, is_training=False,
                   log_dir=os.path.join(os.environ['HOME'], 'Desktop', 'logs_prediction'))
    m.create_hdf5()
