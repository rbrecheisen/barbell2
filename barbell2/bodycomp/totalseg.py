import os
import subprocess
import logging

logger = logging.getLogger(__name__)


class TotalSegmentator:

    def __init__(self):
        self.input_file = None
        self.output_directory = None
        self.fast = False
        self.statistics = False
        self.radiomics = False
        self.overwrite = True
        self.cmd = None

    @staticmethod
    def is_empty(directory):
        return len(os.listdir(directory)) == 0

    def execute(self):
        logger.info('Running TotalSegmentator...')
        if self.input_file is None:
            logger.error('Input NIFTI file not specified')
            return None
        if self.output_directory is None:
            logger.error('Output directory not specified')
            return None
        if not self.overwrite and not self.is_empty(self.output_directory):
            logger.info('Overwrite = False and output directory not empty, so skipping')
            return self.output_directory
        fast = ''
        if self.fast:
            fast = '--fast'
        statistics = ''
        if self.statistics:
            statistics = '--statistics'
        radiomics = ''
        if self.radiomics:
            radiomics = '--radiomics'
        self.cmd = 'TotalSegmentator {} {} {} -i {} -o {}'.format(
            statistics, 
            radiomics,
            fast,
            self.input_file,
            self.output_directory,
        )
        logger.info(f'Running command: {self.cmd}')
        os.system(self.cmd)
        return self.output_directory


# class TotalSegmentator:

#     def __init__(self, nifti_path, output_dir):
#         self.nifti_path = nifti_path
#         self.output_dir = output_dir
#         self.fast = False
#         self.statistics = True
#         self.radiomics = False
#         # Check installation of Total Segmentator 
#         try:
#             subprocess.call(['TotalSegmentator'])
#         except FileNotFoundError:
#             logger.error(
#                 'TotalSegmentator is not installed!\n'
#                 'Please install it using pip install pytorch totalsegmentator'
#             )

#     def execute(self):
#         fast = ''
#         if self.fast:
#             fast = '--fast'
#         statistics = ''
#         if self.statistics:
#             statistics = '--statistics'
#         radiomics = ''
#         if self.radiomics:
#             radiomics = '--radiomics'
#         # Build command
#         cmd = 'TotalSegmentator {} {} {} -i {} -o {}'.format(
#             statistics, 
#             radiomics,
#             fast,
#             self.nifti_path,
#             self.output_dir,
#         )
#         logger.info(f'Running command: {cmd}')
#         os.system(cmd)


if __name__ == '__main__':
    def main():
        ts = TotalSegmentator('', '')
    main()
