import os
import logging

from barbell2.converters import DicomToNifti
from barbell2.bodycomp import TotalSegmentator, RoiSelector, SliceSelector, \
    MuscleFatSegmentator, BodyCompositionCalculator

logger = logging.getLogger(__name__)


d2n = DicomToNifti()
d2n.input_directory = '/mnt/localscratch/cds/rbrecheisen/raw/'
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
