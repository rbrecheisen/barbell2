import os
import pytest

from barbell2.createh5 import CreateH5

base_dir = '{}/data/surfdrive/projects/20210203_autosegl3'.format(os.environ['HOME'])


def clean_up():
    if os.path.isfile('train.h5'):
        os.remove('train.h5')
    if os.path.isfile('test.h5'):
        os.remove('test.h5')
    if os.path.isfile('predict.h5'):
        os.remove('predict.h5')


def test_train_test():
    """ Both DICOM and TAG files should be collected and the data split up in a training and test set. """
    clean_up()
    d = os.path.join(base_dir, 'dicom_and_tag')
    args = {
        'data_dir': d,
        'rows': 512, 'columns': 512,
        'type': 'train',
        'test_size': 0.2,
        'log_dir': '.',
    }
    x = CreateH5(args)
    x.execute()
    assert os.path.isfile('train.h5')
    assert os.path.isfile('test.h5')
    clean_up()


def test_train():
    """ Both DICOM and TAG files should be collected but all data used for training. """
    clean_up()
    d = os.path.join(base_dir, 'dicom_and_tag')
    args = {
        'data_dir': d,
        'rows': 512, 'columns': 512,
        'type': 'train',
        'test_size': 0.0,
        'log_dir': '.',
    }
    x = CreateH5(args)
    x.execute()
    assert os.path.isfile('train.h5')
    clean_up()


def test_predict():
    """ Only DICOM files should be collected for prediction of labels. """
    clean_up()
    d = os.path.join(base_dir, 'dicom')
    args = {
        'data_dir': d,
        'rows': 512, 'columns': 512,
        'type': 'predict',
        'test_size': 0.0,
        'log_dir': '.',
    }
    x = CreateH5(args)
    x.execute()
    assert os.path.isfile('predict.h5')
    clean_up()
