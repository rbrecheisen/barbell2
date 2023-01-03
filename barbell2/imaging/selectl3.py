import os
import shutil
import pydicom
import nibabel
import numpy as np


class L3Selector:

    def __init__(self, dicom_series_dir, nifti_image, nifti_roi, alpha=0.68):
        """ Searches for L3 image in given DICOM series folder based on the L3 vertebra segmentation. This is done
        by first searching for the first and last image slices in the NIFTI image that intersect the NIFTI 
        ROI (L3 vertebra). The image slice indices are then converted to Z-coordinates using the voxel-to-patient
        coordinate transformation of the NIFTI header. To determine the exact L3 image for body composition the
        :param dicom_series_dir: Folder containing all (and only) DICOM files for a given series
        :param nifti_image: File path to NIFTI file created from DICOM series
        :param nifti_roi: File path to NIFTI region-of-interest for segmented L3 vertebral body
        :return: File path to the L3 image
        """
        self.dicom_series_dir = dicom_series_dir
        self.nifti_image = nifti_image
        self.nifti_roi = nifti_roi
        self.alpha = alpha

    @staticmethod
    def get_min_max_slice_idx_nifti_roi(nifti_roi):
        nifti_roi_data = nifti_roi.get_fdata()
        nr_slices = nifti_roi_data.shape[2]
        i_min = -1
        for i in range(nr_slices):
            slice = nifti_roi_data[:,:,i]
            if 1 in np.unique(slice):
                i_min = i
                break
        i_max = -1
        for i in range(nr_slices):
            slice = nifti_roi_data[:,:,nr_slices-i-1]
            if 1 in np.unique(slice):
                i_max = nr_slices - i
                break
        return i_min, i_max

    @staticmethod
    def get_min_max_z_coord_patient_position_nifti_image(i_min, i_max, nifti_image):
        M = nifti_image.affine[:3, :3]
        abc = nifti_image.affine[:3, 3]
        return (M.dot([0, 0, i_min]) + abc)[2], (M.dot([0, 0, i_max]) + abc)[2]

    @staticmethod
    def calculate_estimated_z_coord_l3(z_min, z_max, alpha):
        return z_min + alpha * (z_max - z_min)

    @staticmethod
    def get_nearest_dicom_image_for_estimated_z_coord(dicom_dir, estimated_z_coord):
        z_list = []
        for f in os.listdir(dicom_dir):
            f_path = os.path.join(dicom_dir, f)
            p = pydicom.dcmread(f_path, stop_before_pixels=True)
            z_list.append(p.ImagePositionPatient[2])
        z_nearest = min(z_list, key=lambda x:abs(x - estimated_z_coord))
        for f in os.listdir(dicom_dir):
            f_path = os.path.join(dicom_dir, f)
            p = pydicom.dcmread(f_path, stop_before_pixels=True)
            if p.ImagePositionPatient[2] == z_nearest:
                return f_path
        return None

    def execute(self):
        nifti_roi = nibabel.load(self.nifti_roi)
        i_min, i_max = self.get_min_max_slice_idx_nifti_roi(nifti_roi)
        nifti_image = nibabel.load(self.nifti_image)
        z_min, z_max = self.get_min_max_z_coord_patient_position_nifti_image(i_min, i_max, nifti_image)
        z_estimated = self.calculate_estimated_z_coord_l3(z_min, z_max, self.alpha)
        print(f'i_min: {i_min}, i_max: {i_max}, z_min: {z_min}, z_max: {z_max}, z_estimated: {z_estimated}')
        l3_path = self.get_nearest_dicom_image_for_estimated_z_coord(self.dicom_series_dir, z_estimated)
        print(f'Found L3: {l3_path}')
        return l3_path


if __name__ == '__main__':
    def main():
        selector = L3Selector(
            '/Users/Ralph/Desktop/l3select/ct-abdomen',
            '/Users/Ralph/Desktop/l3select/ct-abdomen.nii.gz',
            '/Users/Ralph/Desktop/l3select/l3.nii.gz',
        )
        x = selector.execute()
        print(x)
    main()
