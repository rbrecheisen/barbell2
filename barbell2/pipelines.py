import os
import logging

from barbell2.converters import DicomToNifti
from barbell2.bodycomp import TotalSegmentator, RoiSelector, SliceSelector

logger = logging.getLogger(__name__)



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
