import os
import subprocess
import logging

logger = logging.getLogger(__name__)


class TotalSegmentator:

    def __init__(self, nifti_path, output_dir):
        self.nifti_path = nifti_path
        self.output_dir = output_dir
        self.fast = False
        self.statistics = True
        self.radiomics = False
        # Check installation of Total Segmentator 
        try:
            subprocess.call(['TotalSegmentator'])
        except FileNotFoundError:
            logger.error(
                'TotalSegmentator is not installed!\n'
                'Please install it using pip install pytorch totalsegmentator'
            )

    def execute(self):
        fast = ''
        if self.fast:
            fast = '--fast'
        statistics = ''
        if self.statistics:
            statistics = '--statistics'
        radiomics = ''
        if self.radiomics:
            radiomics = '--radiomics'
        # Build command
        cmd = 'TotalSegmentator {} {} {} -i {} -o {}'.format(
            statistics, 
            radiomics,
            fast,
            self.nifti_path,
            self.output_dir,
        )
        logger.info(f'Running command: {cmd}')
        os.system(cmd)


if __name__ == '__main__':
    def main():
        ts = TotalSegmentator('', '')
    main()
