import os

from .dcm2masks import Dcm2Masks
from .dcm2nifti import Dcm2Nifti
from .dcm2numpy import Dcm2Numpy
from .nifti2masks import Nifti2Masks
from .tag2dcm import Tag2Dcm
from .tag2nifti import Tag2Nifti
from .tag2numpy import Tag2NumPy

from pydicom._dicom_dict import DicomDictionary


def is_dicom_file(file_path):
    if not os.path.isfile(file_path):
        return False
    if file_path.startswith('._'):
        return False
    try:
        with open(file_path, "rb") as f:
            return f.read(132).decode("ASCII")[-4:] == "DICM"
    except UnicodeDecodeError:
        return False


def is_tag_file(file_path):
    return file_path.endswith('.tag') and not file_path.startswith('._')


def tag_for_name(name):
    for key, value in DicomDictionary.items():
        if name == value[4]:
            return hex(int(key))
    return None


def get_dictionary_items():
    return DicomDictionary.items()
