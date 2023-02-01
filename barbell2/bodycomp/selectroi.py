import os
import shutil
import logging

logger = logging.getLogger(__name__)


class RoiSelector:

    VERTEBRAE_T4 = 'vertebrae_T4.nii.gz'
    VERTEBRAE_L2 = 'vertebrae_L2.nii.gz'
    VERTEBRAE_L3 = 'vertebrae_L3.nii.gz'
    VERTEBRAE_L4 = 'vertebrae_L4.nii.gz'

    def __init__(self):
        self.input_directory = None
        self.roi = None
        self.output_directory = None
        self.output_file = None

    def execute(self):
        if self.input_directory is None:
            logger.error('Input directory not specified')
            return None
        if self.roi is None:
            logger.error('ROI not specified')
            return None
        if self.output_directory is None:
            logger.error('Output directory not specified')
            return None
        os.makedirs(self.output_directory, exist_ok=True)
        shutil.copy(os.path.join(self.input_directory, RoiSelector.VERTEBRAE_L3, self.output_directory))
        self.output_file = os.path.join(self.output_directory, RoiSelector.VERTEBRAE_L3)
        return self.output_file
