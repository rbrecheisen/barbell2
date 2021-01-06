import os
import datetime


class MyException(Exception):
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
        message = '[' + now.strftime('%Y-%m-%d %H:%M:%S.%f') + '] ' + message
        print(message)
        if self.f:
            self.f.write(message + '\n')

    def __del__(self):
        self.f.close()