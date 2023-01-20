import os
import h5py
import argparse
import numpy as np

from barbell2.imaging.dcm2npy import Dicom2Numpy
from barbell2.imaging.tag2npy import Tag2Numpy
from barbell2.imaging.utils import update_labels, is_dicom_file


def get_dcm_pixels(f):
    d2n = Dicom2Numpy(f)
    d2n.set_normalize_enabled(True)
    return d2n.execute()


def get_tag_pixels_for_dcm(f, shape):
    if f.endswith('.dcm'):
        f_tag = f[:-4] + '.tag'
    else:
        f_tag = f + '.tag'
    t2n = Tag2Numpy(f_tag, shape)
    return t2n.execute()


def has_correct_labels(pixels):
    labels = np.unique(pixels)
    if 0 in labels and 1 in labels and 5 in labels and 7 in labels:
        return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help='Input directory')
    parser.add_argument('--output_file', help='Output file', default='output.h5')
    parser.add_argument('--rows', help='Nr. of rows in images', type=int, default=512)
    parser.add_argument('--cols', help='Nr. of columns in images', type=int, default=512)
    args = parser.parse_args()
    with h5py.File(args.output_file, 'w') as h5f:
        count = 1
        for f in os.listdir(args.input_dir):
            f_path = os.path.join(args.input_dir, f)
            if is_dicom_file(f_path):
                dcm_pixels = get_dcm_pixels(f_path)
                tag_pixels = get_tag_pixels_for_dcm(f_path, (args.rows, args.cols))
                if has_correct_labels(tag_pixels):
                    tag_pixels = update_labels(tag_pixels)
                    idd = ':04d'.format(count)
                    group = h5f.create_group(idd)
                    group.create_dataset('image', data=dcm_pixels)
                    group.create_dataset('labels', data=tag_pixels)
                    print(f'{idd}: added {f_path}')
                    count += 1
                else:
                    print(f'[ERROR] missing labels for {f_path}')
    print(f'Created HDF5 based on {count} patients')



if __name__ == '__main__':
    from barbell2.common import setup_args_env
    setup_args_env([
        '--input_dir=/Users/Ralph/data/scalpel/raw/gkroft-colorectal-t4-1',
        '--output_file=/Users/Ralph/Desktop/gkroft-colorectal-t4-1.h5',
        '--rows=512',
        '--cols=512',
    ])
    main()
