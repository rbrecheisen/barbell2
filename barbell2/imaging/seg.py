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
    """ Extracts all slices (as a list of 2D NumPy arrays) in the source NIFTI 
    image that intersect the given ROI. Additionally, it outputs corresponding
    array indexes and DICOM instance numbers, if available in the source image's
    meta data. This requires that the NIFTI image was created from a DICOM series
    using the meta-data option.

    Outputs:
    - List of 2D Numpy arrays
    - List of z- or depth indexes pointing to the 2D arrays inside the volume
    - (optional) List of DICOM instance numbers
     """
    def __init__(self, nifti_path, roi_path):
        self.nifti_path = nifti_path
        self.roi_path = roi_path

    def execute(self):
        pass


class RoiRadiomicsExtractor:
    """ Calculates number of radiomics features on the given ROI. 
    """
    def __init__(self, roi_path):
        pass

    def execute(self):
        pass

    def get_volume(self):
        pass

    def get_mean_pixel_value(self):
        pass


if __name__ == '__main__':
    def main():
        pass
    main()
