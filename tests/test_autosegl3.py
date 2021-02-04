import os

from barbell2.autosegl3 import AutoSegL3


def test_autosegl3():
    params = {
        'image_shape': (512, 512, 1),
        'log_dir': '{}/Desktop'.format(os.environ['HOME']),
        'output_dir': '/tmp/autosegl3',
        'test_size': 0.2,
    }
    d = '{}/data/surfdrive/projects/20210203_autosegl3/dicom_and_tag'.format(os.environ['HOME'])
    tool = AutoSegL3(params=params)
    print(tool.train(d))
