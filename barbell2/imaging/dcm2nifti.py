import os
import subprocess


class Dicom2Nifti:

    def __init__(self, dcm_file_dir_or_path, nii_file_path):
        if os.path.isfile(dcm_file_dir_or_path):
            self.merge_option = '-m n'
        else:
            self.merge_option = '-m y'
        self.dcm_file_dir_or_path = dcm_file_dir_or_path
        items = os.path.split(nii_file_path)
        self.nii_file_name = items[1]
        if self.nii_file_name.endswith('.gz'):
            self.nii_file_name = self.nii_file_name[:-7]
        elif self.nii_file_name.endswith('.nii'):
            self.nii_file_name = self.nii_file_name[:-4]
        else:
            pass
        self.nii_file_dir = items[0]
        self.cmd = f'dcm2niix {self.merge_option} -z y -f {self.nii_file_name} -o {self.nii_file_dir} {self.dcm_file_dir_or_path}'

    def execute(self):
        print(f'Executing command {self.cmd}')
        os.system(self.cmd)


if __name__ == '__main__':
    def main():
        d2n = Dicom2Nifti(
            '/Users/Ralph/data/scalpel/raw/tlodewick-ct-noise-1/AL_100%/101816478/2-Abdomen',
            '/Users/Ralph/data/scalpel/processed/tlodewick-ct-noise-1-out-1/my_nifti.nii.gz',
        )
        d2n.execute()
        print(os.listdir('/Users/Ralph/data/scalpel/processed/tlodewick-ct-noise-1-out-1'))
    main()
