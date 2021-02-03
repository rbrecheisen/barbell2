import os
import unittest
import datetime

from types import SimpleNamespace


class MyException(Exception):
    pass


class MyTestCase(unittest.TestCase):

    def setup(self):
        pass

    def setUp(self):
        self.setup()

    def tear_down(self):
        pass

    def tearDown(self):
        self.tear_down()


class MyTestArguments(SimpleNamespace):
    pass


class Logger(object):

    def __init__(self, file_name_prefix='log_', to_dir='.'):
        self.f = None
        now = datetime.datetime.now()
        file_name = '{}_{}.txt'.format(file_name_prefix, now.strftime('%Y%m%d_%H%M%S'))
        self.f = open(os.path.join(to_dir, file_name), 'w')

    def print(self, message):
        now = datetime.datetime.now()
        message = '[' + now.strftime('%Y-%m-%d %H:%M:%S.%f') + '] ' + str(message)
        print(message)
        if self.f:
            self.f.write(message + '\n')

    def __del__(self):
        self.f.close()
