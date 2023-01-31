import os
import shutil
import logging
import subprocess

logger = logging.getLogger(__name__)


class DicomToNifti:

    def __init__(self):
        self.input_directory = None
        self.output_file = None
        self.cmd = None

    def execute(self, verbose=False):
        if self.input_directory is None:
            logger.error('Input directory not specified')
            return None
        if self.output_file is None:
            logger.error('Output file not specified')
            return None
        try:
            subprocess.call(['dcm2niix'])
        except FileNotFoundError:
            logger.error('Program dcm2niix not found.\nPlease install using following command: \n'
            '  curl -fLO https://github.com/rordenlab/dcm2niix/releases/latest/download/dcm2niix_mac.zip')
            return None
        items = os.path.split(self.output_file)
        output_file_name = items[1]
        if output_file_name.endswith('.nii.gz'):
            output_file_name = output_file_name[:-7]
        elif output_file_name.endswith('.nii'):
            output_file_name = output_file_name[:-4]
        else:
            pass
        output_file_dir = items[0]
        os.makedirs(output_file_dir, exist_ok=True)
        self.cmd = f'dcm2niix -m y -z y -f {output_file_name} -o {output_file_dir} {self.input_directory}'
        if verbose:
            logger.info(f'{self.cmd}')
        os.system(self.cmd)
        return self.output_file


class TotalSegmentator:

    def __init__(self):
        self.input_file = None
        self.output_directory = None
        self.fast = False
        self.statistics = False
        self.radiomics = False


class RoiSelector:

    VERTEBRAE_L3 = 'vertebrae_L3.nii.gz'

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
        pass


class MuscleFatSegmentator:

    def __init__(self):
        self.input_files = None
        self.image_dimensions = None
        self.model = None
        self.output_segmentation_files = None

    def execute():
        pass


class BodyCompositionCalculator:

    def __init__(self):
        self.input_files = None
        self.segmentation_files = None
        self.heights = None
        self.output_metrics = None

    def execute(self):
        pass


d2n = DicomToNifti()
d2n.input_directory = '/Users/ralph/SURF Drive/projects/hpb/bodycomposition/data/ct_noise_recon/AL_100%/101816478/2-Abdomen'
d2n.output_file = '/Users/ralph/Desktop/output/output_file.nii.gz'
d2n.execute()

totalseg = TotalSegmentator()
totalseg.input_file = d2n.output_file
totalseg.output_directory = '/Users/ralph/Desktop/output'
totalseg.fast = True
totalseg.statistics = False
totalseg.radiomics = False
totalseg.execute()

roiselector = RoiSelector()
roiselector.roi = RoiSelector.VERTEBRAE_L3
roiselector.input_directory = totalseg.output_directory
roiselector.output_directory = '/Users/ralph/Desktop/output_roi'
roiselector.execute()

sliceselector = SliceSelector()
sliceselector.input_roi = roiselector.output_file
sliceselector.input_volume = d2n.output_file
sliceselector.input_dicom_directory = d2n.input_directory
sliceselector.mode = SliceSelector.MEDIAN
sliceselector.execute()

seg = MuscleFatSegmentator()
seg.input_files = [sliceselector.output_file]
seg.image_dimensions = (512, 512)
seg.model = 'model.db'
seg.execute()

calculator = BodyCompositionCalculator()
calculator.input_files = [sliceselector.output_file]
calculator.segmentation_files = seg.output_segmentation_files
calculator.execute()

for f in calculator.output_metrics.keys():
    print(f'{f} = {calculator.output_metrics[f]}')
