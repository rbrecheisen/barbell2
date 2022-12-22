import os

class TotalSegmentator:

    def __init__(self, nifti_path, output_dir):
        self.nifti_path = nifti_path
        self.output_dir = output_dir
        self.fast = False
        self.statistics = True
        self.radiomics = False

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
        cmd = 'TotalSegmentator {} {} {} -i {} -o {}'.format(
            statistics, 
            radiomics,
            fast,
            self.nifti_path,
            self.output_dir,
        )
        print(f'Running command: {cmd}')
        os.system(cmd)


class RoiSliceExtractor:
    """ Extracts all slices in the source image that intersect
    the given ROI
     """
    def __init__(self, image_path, roi_path):
        self.image_path = image_path
        self.roi_path = roi_path

    def execute(self):
        pass


if __name__ == '__main__':
    def main():
        pass
    main()
