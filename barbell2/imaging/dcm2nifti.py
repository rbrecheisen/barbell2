import os
import shutil
import pydicom
import dcmstack

from dcmstack import dcmmeta


class Dicom2Nifti:

    def __init__(self, dcm_file_dir, nii_file_path):
        self.dcm_file_dir = dcm_file_dir
        items = os.path.split(nii_file_path)
        self.nii_file_name = items[1]
        if self.nii_file_name.endswith('.gz'):
            self.nii_file_name = self.nii_file_name[:-7]
        elif self.nii_file_name.endswith('.nii'):
            self.nii_file_name = self.nii_file_name[:-4]
        else:
            pass
        self.nii_file_dir = items[0]
        self.cmd = f'dcm2niix -m y -z y -f {self.nii_file_name} -o {self.nii_file_dir} {self.dcm_file_dir}'

    def execute(self):
        print(f'Executing command {self.cmd}')
        os.system(self.cmd)


class Dicom2NiftiWithHeaderInfo:

    def __init__(self, dcm_file_dir, nii_file):
        self.dcm_file_dir = dcm_file_dir
        self.nii_file = nii_file

    def execute(self):
        files = [os.path.join(self.dcm_file_dir, f) for f in os.listdir(self.dcm_file_dir)]
        # https://dcmstack.readthedocs.io/en/v0.6.1/Python_Tutorial.html#looking-up-meta-data
        stacks = dcmstack.parse_and_stack(files, group_by='SeriesInstanceUID')
        stack = list(stacks.values())[0]
        nii = stack.to_nifti(embed_meta=True)
        nii.to_filename(self.nii_file)
        # nii_meta = dcmmeta.NiftiWrapper.from_filename('file.nii.gz')
        # for i in range(nr_slices):
        #     instance_nr = nii_meta.get_meta('InstanceNumber', index=(0, 0, i))
        #     if instance_nr == 100:
        #         image = nii_meta.nii_img.dataobj[:,:,i]
        #         print(f'found image! {image.shape}')
        #         n2p = npy2png.Numpy2Png(image)
        #         n2p.set_output_dir('/Users/Ralph/Desktop')
        #         n2p.set_png_file_name('f_100.dcm.png')
        #         n2p.execute()
        #         break


if __name__ == '__main__':
    def main():
        # d2n = Dicom2Nifti(
        #     '/Users/Ralph/data/scalpel/raw/tlodewick-ct-noise-1/AL_100%/101816478/2-Abdomen',
        #     '/Users/Ralph/data/scalpel/processed/tlodewick-ct-noise-1-out-1/my_nifti.nii.gz',
        # )
        # d2n.execute()
        # print(os.listdir('/Users/Ralph/data/scalpel/processed/tlodewick-ct-noise-1-out-1'))
        d2n = Dicom2NiftiWithHeaderInfo(
            '/Users/Ralph/Desktop/itk/ct-abdomen',
            '/Users/Ralph/Desktop/itk/out/ct-abdomen.nii.gz',
        )
        d2n.execute()
    main()
