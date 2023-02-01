import os
import logging

logger = logging.getLogger(__name__)


class SliceSelector:

    ALL = 0
    IQR_25 = 1
    IQR_50 = 2
    IQR_75 = 3
    MEDIAN = IQR_50

    def __init__(self):
        self.input_roi = None
        self.input_volume = None
        self.input_dicom_directory = None
        self.mode = None
        self.output_file = None

    def execute(self):
        if self.input_roi is None:
            logger.error('Input ROI not specified')
            return None
        if self.input_volume is None:
            logger.error('Input NIFTI volume not specified')
            return None
        if self.input_dicom_directory is None:
            logger.error('Input DICOM directory not specified')
            return None
        if self.mode is None:
            logger.error('Mode not specified')
            return None
        pass


if __name__ == '__main__':
    def main():
        selector = SliceSelector()
        selector.input_roi = '/Users/Ralph/Desktop/auto-vs-manual-l3/segmentations/al/vertebrae_L3.nii.gz'
        selector.input_volume = '/Users/Ralph/Desktop/auto-vs-manual-l3/scans_prep_nifti/al.nii.gz'
        selector.input_dicom_directory = '/Users/Ralph/Desktop/auto-vs-manual-l3/scans_prep/al'
        selector.mode = SliceSelector.MEDIAN
        selector.execute()
    main()
