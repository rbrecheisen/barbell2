import os
import shutil
import pydicom
import pydicom.errors
import argparse

from barbell2.imaging.utils import get_tag_file_for_dicom


def get_variable_operator_value(vc):
    if '==' in vc:
        items = [x.strip() for x in vc.split('==')]
        return items[0], '==', items[1]
    if '>=' in vc:
        items = [x.strip() for x in vc.split('>=')]
        return items[0], '>=', items[1]
    if '<=' in vc:
        items = [x.strip() for x in vc.split('<=')]
        return items[0], '<=', items[1]
    if '>' in vc:
        items = [x.strip() for x in vc.split('>')]
        return items[0], '>', items[1]
    if '<' in vc:
        items = [x.strip() for x in vc.split('<==>')]
        return items[0], '<', items[1]
    raise RuntimeError(f'Illegal value constraint: {vc}')


def dicom_ok(p, args):
    attributes = [x.strip() for x in args.attributes.split(',')]
    for attribute in attributes:
        if attribute not in p:
            return False, f'Attribute {attribute} missing'
    value_constraints = [x.strip() for x in args.values.split(',')]
    for vc in value_constraints:
        var, op, val = get_variable_operator_value(vc)
        val_p = str(p[var].value)
        if op == '==':
            if val_p != val:
                return False, f'Attribute {var} != {val} ({val_p})'
        if op == '<=':
            if val_p > val:
                return False, f'Attribute {var} > {val} ({val_p})'
        if op == '>=':
            if val_p < val:
                return False, f'Attribute {var} < {val} ({val_p})'
        if op == '<':
            if val_p >= val:
                return False, f'Attribute {var} >= {val} ({val_p})'
        if op == '>':
            if val_p <= val:
                return False, f'Attribute {var} <= {val} ({val_p})'
    return True, None


def main():
    """ This script filters a directory with DICOM files (and possible TAG files) checking
    the headers for mandatory information, like rows, columns, pixel spacing, etc. It's
    important that TAG files are also copied whenever a DICOM file is ok.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help='Input directory', default='.')
    parser.add_argument('--output_dir', help='Output directory', default='output')
    parser.add_argument(
        '--attributes', help='Attributes that must be present',
        default='Rows,Columns,PixelSpacing,BitsStored,BitsAllocated,RescaleSlope,RescaleIntercept')
    parser.add_argument(
        '--values', help='Value constraints', default='Rows==512,Columns==512,BitsStored>=12,BitsStored<=16')
    args = parser.parse_args()
    os.makedirs(args.output_dir)
    errors = []
    for f in os.listdir(args.input_dir):
        f_path = os.path.join(args.input_dir, f)
        f_path_new = os.path.join(args.output_dir, f)
        try:
            p = pydicom.dcmread(f_path, stop_before_pixels=True)
            result, msg = dicom_ok(p, args)
            if result:
                # Copy DICOM and TAG file to output directory
                shutil.copy(f_path, f_path_new)
                tag_file = get_tag_file_for_dicom(f_path)
                if os.path.isfile(tag_file):
                    tag_name = os.path.split(tag_file)[1]
                    shutil.copy(tag_file, os.path.join(args.output_dir, tag_name))
                    print(f'{f_path}|*.tag')
                else:
                    print(f'{f_path}')
            else:
                errors.append(f'{f_path}: {msg}')
        except pydicom.errors.InvalidDicomError:
            pass
    if len(errors) > 0:
        with open(os.path.join(args.output_dir, 'errors.txt'), 'w') as f:
            for error in errors:
                f.write(error + '\n')
        print('Errors encountered. See <output_dir>/errors.txt for details')
    else:
        print('No errors')


if __name__ == '__main__':
    from barbell2 import common
    common.setup_args_env([
        '--input_dir=/Users/Ralph/SURF Drive/projects/hpb/bodycomposition/data/l3tag_cohorts/SURG-PANC',
        '--output_dir=/Users/Ralph/Desktop/output',
    ])
    main()

# parser.add_argument(
#     '--mandatory_values', help='Values attributes must have', default='Rows=512,Columns=512')
# args = parser.parse_args()
# mandatory_attributes = [x.strip() for x in args.mandatory_attributes.split(',')]
# mandatory_values = [x.strip() for x in args.mandatory_values.split(',')]
# mandatory_values_dict = {}
# for value in mandatory_values:
#     items = [x.strip() for x in value.split('=')]
#     mandatory_values_dict[items[0]] = items[1]
# os.makedirs(args.output_dir)
# os.makedirs(args.output_dir_error)
# files_ok = []
# files_error = []
# for f in os.listdir(args.input_dir):
#     f_path = os.path.join(args.input_dir, f)
#     try:
#         error = False
#         p = pydicom.dcmread(f_path, stop_before_pixels=True)
#         for attribute in mandatory_attributes:
#             if attribute not in p:
#                 error = True
#                 files_error.append(f_path)
#                 print(f'Attribute {attribute} not in {f_path}')
#         for k, v in mandatory_values_dict.items():
#             v_p = str(p[k].value)
#             if v_p != v:
#                 error = True
#                 files_error.append(f_path)
#                 print(f'Value {v_p} of {k} should be {v}')
#         if not error:
#             files_ok.append(f_path)
#     except pydicom.errors.InvalidDicomError:
#         pass
# for f in files_ok:
#     shutil.copy(f, os.path.join(args.output_dir_error, os.path.split(f)[1]))
#     shutil.copy(f, os.path.join(args.output_dir, os.path.split(f)[1]))
# for f in files_error:
