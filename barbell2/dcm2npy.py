import pydicom

from barbell2.utils import apply_window


class Dicom2Numpy:

    def __init__(self, dcm_file_path_or_obj):
        self.dcm_file_path_or_obj = dcm_file_path_or_obj
        self.npy_array = None
        self.window = None
        self.normalize_enabled = True

    def set_window(self, window):
        self.window = window

    def set_normalize_enabled(self, normalize_enabled):
        self.normalize_enabled = normalize_enabled

    def is_normalize_enabled(self):
        return self.normalize_enabled

    def execute(self):
        self.npy_array = None
        if isinstance(self.dcm_file_path_or_obj, str):
            p = pydicom.dcmread(self.dcm_file_path_or_obj)
        else:
            p = self.dcm_file_path_or_obj
        pixels = p.pixel_array
        self.npy_array = pixels.reshape(p.Rows, p.Columns)
        if self.is_normalize_enabled():
            b = p.RescaleIntercept
            m = p.RescaleSlope
            self.npy_array = m * self.npy_array + b
        if self.window is not None:
            self.npy_array = apply_window(self.npy_array, self.window)
        return self.npy_array
