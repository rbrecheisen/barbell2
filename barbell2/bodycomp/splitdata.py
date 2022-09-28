import os
import shutil
import argparse

from random import shuffle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help='Input directory', default='.')
    parser.add_argument('--output_dir', help='Output directory', default='output')
    parser.add_argument(
        '--nr_folds', help='Number of folds in cross-validation (0 means no CV)', type=int, default=0)
    parser.add_argument('--test_size', help='Percentage to use for testing', type=float, default=0.25)
    parser.add_argument('--validation_size', help='Percentage to use for validation/tuning', type=float, default=0)
    parser.add_argument('--shuffle', help='Whether to shuffle files before splitting', type=int, default=1)
    args = parser.parse_args()
    training_size = 1.0 - args.validation_size - args.test_size
    assert training_size >= 0.25, f'Training size < 25% ({training_size})'
    if args.nr_folds > 0:
        assert args.nr_folds >= 3, f'Number of cross-validation folds < 3 ({args.nr_folds})'
    os.makedirs(args.output_dir)

    # TODO: Shuffle taking DICOM and TAG file pairs into account!!!
    # Load DICOM/TAG file pairs together
    # all_files = []
    # for f in os.listdir(args.input_dir):
    #     f_path = os.path.join(args.input_dir, f)
    #     all_files.append(f_path)
    # if args.shuffle == 1:
    #     shuffle(all_files)
    # nr_test = int(args.test_size * len(all_files))
    # nr_validation = int(args.validation_size * len(all_files))
    # nr_train = len(all_files) - nr_validation - nr_test
    # if nr_train > 0:
    #     os.makedirs(os.path.join(args.output_dir, 'training'))
    #     for i in range(nr_train):
    #         f_path = all_files.pop(0)
    #         f_name = os.path.split(f_path)[1]
    #         f_path_new = os.path.join(args.output_dir, 'training', f_name)
    #         shutil.copy(f_path, f_path_new)
    # if nr_validation > 0:
    #     os.makedirs(os.path.join(args.output_dir, 'validation'))
    #     for i in range(nr_validation):
    #         f_path = all_files.pop(0)
    #         f_name = os.path.split(f_path)[1]
    #         f_path_new = os.path.join(args.output_dir, 'validation', f_name)
    #         shutil.copy(f_path, f_path_new)
    # if nr_test > 0:
    #     os.makedirs(os.path.join(args.output_dir, 'testing'))
    #     for i in range(nr_test):
    #         f_path = all_files.pop(0)
    #         f_name = os.path.split(f_path)[1]
    #         f_path_new = os.path.join(args.output_dir, 'testing', f_name)
    #         shutil.copy(f_path, f_path_new)


if __name__ == '__main__':
    from barbell2 import common
    common.setup_args_env([
        '--input_dir=/Users/Ralph/SURF Drive/projects/hpb/bodycomposition/data/l3tag_cohorts/SURG-PANC',
        '--output_dir=/Users/Ralph/Desktop/output',
        '--test_size=0.2',
        '--validation_size=0.1',
    ])
    main()
