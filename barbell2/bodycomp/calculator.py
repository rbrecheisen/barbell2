import os
import logging

logger = logging.getLogger(__name__)


class BodyCompositionCalculator:

    def __init__(self):
        self.input_files = None                 # L3 images
        self.input_segmentation_files = None    # Segmentations calculated using MuscleFatSegmentator
        self.heights = None                     # (Optional) dictionary containing heights for each L3 image
        self.output_metrics = None              # Dictionary containing output metrics for each L3 image

    def execute(self):
        if self.input_files is None:
            logger.error('Input files not specified')
            return None
        if self.input_segmentation_files is None:
            logger.error('Input segmentation files not specified')
            return None
        # Check that we're not dealing with probability maps
        if self.input_segmentation_files[0].endswith('.seg.prob.npy'):
            logger.error('Cannot handle *.seg.prob.npy files')
            return None
        # Check that for each input file we have a matching segmentation file
        file_pairs = []
        for input_file in self.input_files:
            input_file_name = os.path.split(input_file)[1]
            found = False
            for input_segmentation_file in self.input_segmentation_files:
                input_segmentation_file_name = os.path.split(input_segmentation_file)[1]
                if input_file_name + '.seg.npy' == input_segmentation_file_name:
                    file_pairs.append(input_file, input_segmentation_file)
                    found = True
                    break
            if not found:
                logger.warn(f'Input file {input_file_name} missing corresponding segmentation file')
        # Work with found file pairs
        self.output_metrics = {}
        for file_pair in file_pairs:
            self.output_metrics[file_pair[0]] = {
                
            }