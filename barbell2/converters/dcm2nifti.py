import os
import logging
import subprocess

logger = logging.getLogger(__name__)

# import dcmstack
# from dcmstack import dcmmeta


class DicomToNifti:

    def __init__(self):
        try:
            subprocess.call(['dcm2niix'])
        except FileNotFoundError:
            print(
                'dcm2niix is not installed! Please install it using the following command:\n'
                'curl -fLO https://github.com/rordenlab/dcm2niix/releases/latest/download/dcm2niix_mac.zip'
            )
        self.input_directory = None
        self.output_file = None
        self.cmd = None

    def execute(self, verbose=False):
        if self.input_directory is None:
            logger.error('Input directory not specified')
            return None
        if self.output_file is None:
            logger.error('Output file not specified')
            return None
        items = os.path.split(self.output_file)
        output_file_name = items[1]
        if output_file_name.endswith('.nii.gz'):
            output_file_name = output_file_name[:-7]
        elif output_file_name.endswith('.nii'):
            output_file_name = output_file_name[:-4]
        else:
            pass
        output_file_dir = items[0]
        os.makedirs(output_file_dir, exist_ok=True)
        self.cmd = f'dcm2niix -m y -z y -f {output_file_name} -o {output_file_dir} {self.input_directory}'
        if verbose:
            logger.info(f'{self.cmd}')
        os.system(self.cmd)
        return self.output_file


# class Dicom2Nifti:

#     def __init__(self, dcm_file_dir, nii_file_path):
#         try:
#             subprocess.call(['dcm2niix'])
#         except FileNotFoundError:
#             print(
#                 'dcm2niix is not installed! Please install it using the following command:\n'
#                 'curl -fLO https://github.com/rordenlab/dcm2niix/releases/latest/download/dcm2niix_mac.zip'
#             )
#         self.dcm_file_dir = dcm_file_dir
#         items = os.path.split(nii_file_path)
#         self.nii_file_name = items[1]
#         if self.nii_file_name.endswith('.gz'):
#             self.nii_file_name = self.nii_file_name[:-7]
#         elif self.nii_file_name.endswith('.nii'):
#             self.nii_file_name = self.nii_file_name[:-4]
#         else:
#             pass
#         self.nii_file_dir = items[0]
#         self.cmd = f'dcm2niix -m y -z y -f {self.nii_file_name} -o {self.nii_file_dir} {self.dcm_file_dir}'

#     def execute(self):
#         print(f'Executing command: {self.cmd}')
#         os.system(self.cmd)


# class Dicom2NiftiWithHeaderInfo:

#     def __init__(self, dcm_file_dir, nifti_file):
#         self.dcm_file_dir = dcm_file_dir
#         self.nifti_file = nifti_file

#     def execute(self):
#         files = [os.path.join(self.dcm_file_dir, f) for f in os.listdir(self.dcm_file_dir)]
#         # https://dcmstack.readthedocs.io/en/v0.6.1/Python_Tutorial.html#looking-up-meta-data
#         stacks = dcmstack.parse_and_stack(files, group_by='SeriesInstanceUID')
#         stack = list(stacks.values())[0]
#         nii = stack.to_nifti(embed_meta=True)
#         nii.to_filename(self.nifti_file)
#         return self.nifti_file


if __name__ == '__main__':
    def main():
        d2n = Dicom2Nifti(
            '/Users/Ralph/data/scalpel/raw/tlodewick-ct-noise-1/AL_100%/101816478/2-Abdomen',
            '/Users/Ralph/data/scalpel/processed/tlodewick-ct-noise-1-out-1/my_nifti.nii.gz',
        )
        d2n.execute()
        print(os.listdir('/Users/Ralph/data/scalpel/processed/tlodewick-ct-noise-1-out-1'))
        d2n.print_metainfo()
        # d2n = Dicom2NiftiWithHeaderInfo(
        #     '/Users/Ralph/Desktop/itk/ct-abdomen',
        #     '/Users/Ralph/Desktop/itk/out/ct-abdomen.nii.gz',
        # )
        # d2n.execute()
    main()
