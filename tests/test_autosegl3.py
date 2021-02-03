import os

from barbell2 import AutoSegL3


def test_autosegl3():
    params = {'test_size': 0.2, 'image_shape': (512, 512, 1)}
    tool = AutoSegL3(params=params)
    tool.train('{}/data/surfdrive/projects/20210203_autosegl3/dicom_and_tag'.format(os.environ['HOME']))
