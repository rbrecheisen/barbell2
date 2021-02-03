import os

from barbell2 import CreateHDF5


def test_create_hdf5():

    m = CreateHDF5(
        '/Users/Ralph/data/surfdrive/projects/20210203_autosegl3/training',
        '/Users/Ralph/data/surfdrive/projects/20210203_autosegl3/training.h5',
        512, 512, 0.8,
        os.path.join(os.environ['HOME'], 'Desktop'),
    )

    m.create_hdf5()
