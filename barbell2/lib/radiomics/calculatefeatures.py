import os
import json
import numpy as np
import SimpleITK as sitk
from radiomics import featureextractor


class CalculateFeatures(object):

    def __init__(self):
        self._input_image_file_path = None
        self._input_mask_file_path = None
        self._wavelet_enabled = False
        self._log_enabled = False
        self._log_custom_args = None
        self._2d = True
        self._3d = False
        self._output_dir = None
        self._settings = {}
        self._settings_file_path = None
        self._apply_slope_and_intercept = True
        self._output_file_path = None

    # INTERFACE

    def set_input_image_file_path(self, file_path):
        self._input_image_file_path = file_path

    def set_input_mask_file_path(self, file_path):
        self._input_mask_file_path = file_path

    def set_wavelet_enabled(self, value):
        self._wavelet_enabled = value

    def set_log_enabled(self, value):
        if value and self._2d:
            raise RuntimeError('Set calculation to 3D to allow Log of Gaussian (LoG) features')
        self._log_enabled = value

    def set_log_custom_args(self, custom_args):
        if self._2d:
            raise RuntimeError('Set calculation to 3D to allow Log of Gaussian (LoG) features')
        self._log_custom_args = custom_args

    def apply_default_log_custom_args(self):
        self.set_log_custom_args({'sigma': [1.0, 2.0, 3.0, 4.0, 5.0]})

    def set_2d(self):
        if self._log_enabled:
            raise RuntimeError('Disable Log of Gaussian (LoG) features before calculating 2D radiomics')
        self._2d = True
        self._3d = False
        self.set_setting('force2D', True)

    def set_3d(self):
        self._2d = False
        self._3d = True
        self.set_setting('force2D', False)

    def set_output_dir(self, output_dir):
        self._output_dir = output_dir

    def set_settings(self, settings):
        self._settings = settings

    def set_settings_file_path(self, file_path):
        self._settings_file_path = file_path

    def set_setting(self, name, value):
        self._settings[name] = value

    def set_apply_slope_and_intercept_enabled(self, value):
        self._apply_slope_and_intercept = value

    def apply_default_settings(self):
        self.set_setting('interpolator', sitk.sitkBSpline)
        self.set_setting('resampledPixelSpacing', None)
        self.set_setting('padDistance', 10)
        self.set_setting('resegmentRange', [-3, 3])
        self.set_setting('resegmentMode', 'sigma')
        self.set_setting('voxelArrayShift', 1000)
        self.set_setting('label', 1)

    def get_output_file_path(self):
        return self._output_file_path

    # INTERNAL METHODS

    @staticmethod
    def match_orientations(image, mask, file_name):
        # This function checks whether the sign of the orientations of image and mask match with
        # each other. If not, the directions are flipped in the mask.
        img_dir = image.GetDirection()
        msk_dir = mask.GetDirection()
        new_dir = list(msk_dir)
        for i in range(len(img_dir)):
            x, y = np.sign(img_dir[i]), np.sign(msk_dir[i])
            if x != y:
                print('Mismatching orientation image and mask: {} <> {}'.format(x, y))
                new_dir[i] = -1.0 * msk_dir[i]
        mask.SetDirection(tuple(new_dir))
        return image, mask

    def _load_image_and_mask_files(self, image_file, mask_file):
        image = sitk.ReadImage(image_file)
        mask = sitk.ReadImage(mask_file)
        # Check that orientation of image and mask is the same and correct it if not
        image, mask = self.match_orientations(image, mask, file_name=os.path.split(image_file)[1])
        return image, mask

    @staticmethod
    def _write_features(features, file_path):
        with open(file_path, 'w') as f:
            for k in features.keys():
                f.write(k + ' = ' + str(features[k]))
                f.write('\n')
        return file_path

    # EXECUTE

    def execute(self, verbose=False):
        image, mask = self._load_image_and_mask_files(self._input_image_file_path, self._input_mask_file_path)
        if self._settings_file_path:
            extractor = featureextractor.RadiomicsFeatureExtractor(self._settings_file_path)
        else:
            extractor = featureextractor.RadiomicsFeatureExtractor(**self._settings)
        extractor.enableImageTypeByName('Original')
        if self._wavelet_enabled:
            extractor.enableImageTypeByName('Wavelet')
        extractor.enableAllFeatures()
        if self._log_enabled:
            extractor.enableImageTypeByName('LoG', customArgs=self._log_custom_args)
        features = extractor.execute(image, mask)
        os.makedirs(self._output_dir, exist_ok=True)
        if verbose:
            print(json.dumps(features, indent=4))
        file_name = os.path.split(self._input_mask_file_path)[1]
        if file_name.endswith('.nii.gz'):
            file_name = file_name[:-7] + '.txt'
            file_path = os.path.join(self._output_dir, file_name)
            file_path = self._write_features(features, file_path)
            self._output_file_path = file_path
            if verbose:
                print(file_path)
        elif file_name.endswith('.dcm'):
            file_name = file_name[:-4] + '.txt'
            file_path = os.path.join(self._output_dir, file_name)
            file_path = self._write_features(features, file_path)
            self._output_file_path = file_path
            if verbose:
                print(file_path)
        else:
            raise RuntimeError('Unsupported mask file extension {}'.format(
                os.path.splitext(self._input_mask_file_path)[1]))


if __name__ == '__main__':
    node = CalculateFeatures()
    node.set_2d()
    node.set_input_image_file_path('/Volumes/USB_SECURE1/data/radiomics/projects/004_ovarium/data/test/out/IM_1.nii.gz')
    node.set_input_mask_file_path('/Volumes/USB_SECURE1/data/radiomics/projects/004_ovarium/data/test/out/IM_1_tag_muscle.nii.gz')
    node.set_output_dir('/Volumes/USB_SECURE1/data/radiomics/projects/004_ovarium/data/test/out')
    node.apply_default_settings()
    node.execute()
    print(node.get_output_file_path())
