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

    def __init__(self, to_file=True, to_dir=None):
        self.f = None
        if to_file:
            now = datetime.datetime.now()
            file_name = 'log_{}.txt'.format(now.strftime('%Y%m%d_%H%M%S'))
            if to_dir:
                self.f = open(os.path.join(to_dir, file_name), 'w')
            else:
                self.f = open(file_name, 'w')

    def print(self, message):
        now = datetime.datetime.now()
        message = '[' + now.strftime('%Y-%m-%d %H:%M:%S.%f') + '] ' + str(message)
        print(message)
        if self.f:
            self.f.write(message + '\n')

    def __del__(self):
        self.f.close()
