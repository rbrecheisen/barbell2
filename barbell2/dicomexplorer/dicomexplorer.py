import os
import pydicom
from pydicom._dicom_dict import DicomDictionary
from barbell2.lib import BasicShell


INTRO = """
Welcome to the DICOM Explorer!
------------------------------
This tool allows you to explore lots of DICOM files at the same time. Type 'help' to view a short list of
commands. Type 'help <command>' to view details about a given command.
"""

PROMPT = '(shell) '


def is_dicom(file_path):
    if not os.path.isfile(file_path):
        return False
    try:
        with open(file_path, "rb") as f:
            return f.read(132).decode("ASCII")[-4:] == "DICM"
    except:
        return False


def get_institute_name(file_path):
    items = os.path.split(file_path)
    institute_name = os.path.split(items[0])[1]
    return institute_name


class DicomExplorerShell(BasicShell):

    def __init__(self):
        super(DicomExplorerShell, self).__init__()
        self.intro = INTRO
        self.prompt = PROMPT
        self.debug = True

    # LOADING FILES AND DIRECTORIES

    def do_load_file(self, file_path):
        """
        Usage: load_file <file name or path>
        Load a single DICOM file. If only the name is provided, it assumed that the file is located in the
        current directory.
        """
        if not os.path.isfile(file_path):
            file_path = os.path.join(self.current_dir, file_path)
        if not is_dicom(file_path):
            self.poutput('File is not DICOM')
            return
        self.poutput('Loading...')
        self.result_manager.add_result_data([file_path])
        self.poutput('Loading done')

    def do_load_dir(self, dir_path):
        """
        Usage: load_dir <dir name or path>
        Load (recursively) all DICOM files in the given directory. If only the directory name is given, it is
        assumed that the directory is located in the current directory.
        """
        if not os.path.isdir(dir_path):
            dir_path = os.path.join(self.current_dir, dir_path)
        self.poutput('Loading {}...'.format(dir_path))
        data = []
        for root, dirs, files in os.walk(dir_path):
            for f in files:
                if not f.startswith('._'):
                    f = os.path.join(root, f)
                    if is_dicom(f):
                        data.append(f)
                        self.poutput(f)
        self.result_manager.add_result_data(data)
        self.poutput('Loading done')

    def do_show_files(self, n):
        """
        Usage: show_files [n]
        Show all (or first n) files loaded in the current result set. If you want to show files from another result set
        select it first using the set_current_result command.
        """
        files = self.result_manager.get_current_result_data()
        n = -1 if n == '' else int(n)
        count = 0
        for f in files:
            self.poutput(f)
            if count == n:
                break
            count += 1
        self.poutput('Total nr. of files: {}'.format(len(files)))

    def do_lookup(self, tag_name):
        """
        Usage: lookup <tag name>
        Lookup tag <tag name> in the DICOM dictionary. You can specify only parts of a tag name, e.g.,
        "Transmit" will return multiple dictionary entries containing the word "Transmit" (like Transmit
        Coil Name). Being able to lookup tags comes in handy when you search for them in DICOM files.
        Note that (parts of) the tag name does not have to be case-sensitive.
        """
        for key, value in DicomDictionary.items():
            output = '{}: {}'.format(key, value)
            if tag_name == '':
                self.poutput(output)
            else:
                for item in value:
                    if tag_name in item:
                        self.poutput(output)

    def do_find_tag(self, tag_name):
        """
        Usage: find_tag <tag name>
        Find tag <tag name> in the currently loaded DICOM files.
        """
        files = self.result_manager.get_current_result_data()
        for f in files:
            p = pydicom.read_file(f)
            for tag in p.keys():
                if tag in list(DicomDictionary.keys()):
                    if tag_name == DicomDictionary[tag][4]:
                        self.poutput('{}: {}'.format(f, p[tag].value))
                        break
                else:
                    self.poutput('Warning: tag {} cannot be found in the DICOM dictionary'.format(tag))

    def do_show_header(self, file_name):
        """
        Usage: show_header <file name>
        Show DICOM header of <file name>. If <file name> is left empty, this function will search for
        all file paths that contain the given file name. If only one is encountered, the DICOM header will
        be displayed. If multiple files are encountered, a list of those files is displayed so that you can
        select a specific one (with its full path).
        """
        files = self.result_manager.get_current_result_data()
        count = 0
        counted_files = []
        for f in files:
            if file_name in f:
                count += 1
                counted_files.append(f)
        if count == 0:
            if os.path.isfile(file_name):
                p = pydicom.read_file(file_name)
                self.poutput(p)
            else:
                self.poutput('Could not find file {}'.format(file_name))
        elif count == 1:
            p = pydicom.read_file(counted_files[0])
            self.poutput(p)
        elif count > 1:
            self.poutput('Found multiple files with same name:')
            for f in counted_files:
                self.poutput(f)
            self.poutput('Please select full file path of file you want and repeat this command')

    def do_check_pixels(self, verbose):
        """
        Usage: check_pixels [verbose]
        Check that each DICOM file contains pixel values that can be loaded using pydicom and NumPy. Sometimes,
        images may be compressed in some way (e.g., using JPEG2000). In that case, they cannot be loaded with
        pydicom and their pixel values need to be extracted to raw format.
        """
        files = self.result_manager.get_current_result_data()
        count = 0
        for f in files:
            p = pydicom.read_file(f)
            try:
                p.convert_pixel_data()
                if verbose != '':
                    self.poutput('OK: {}'.format(f))
            except NotImplementedError:
                count += 1
                self.poutput('ERROR: could not load pixel data {}'.format(f))
        if count > 0:
            self.poutput('Pixel data for {} out of {} files could not be loaded'.format(count, len(files)))
        else:
            self.poutput('Pixel data OK for all files')

    def do_dump_scan_props(self, output_file):
        """
        Usage: dump_scan_props output_file
        Dumps following scanning properties of each DICOM file:

         - Manufacturer (0x8, 0x70)
         - Manufacturer's Model Name (0x8, 0x1090)
         - Software Version(s) (0x18, 0x1020)
         - Exposure Time (0x18, 0x1150)
         - X-Ray Tube Current (0x18, 0x1151)
         - KVP (0x18, 0x60)
         - Slice Thickness (0x18, 0x50)
         - Pixel Spacing (0x28, 0x30)
         - Convolution Kernel (0x18, 0x1210)
         - Filter Type (0x18, 0x1160)
         - Patient Position (0x18, 0x5100)
         - Institution Name (0x8, 0x80)
         - Requested Procedure Description (0x32, 0x1060)

        The output is written to a CSV file for easy analysis.
        """
        files = self.result_manager.get_current_result_data()
        rows = []
        for file_path in files:

            p = pydicom.read_file(file_path)

            manufacturer = ''
            manufacturer_tag = (0x8, 0x70)
            if manufacturer_tag in p:
                manufacturer = p[manufacturer_tag].value

            model_name = ''
            model_name_tag = (0x8, 0x1090)
            if model_name_tag in p:
                model_name = p[model_name_tag].value

            software_version = ''
            software_version_tag = (0x18, 0x1020)
            if software_version_tag in p:
                software_version = p[software_version_tag].value

            exposure_time = ''
            exposure_time_tag = (0x18, 0x1150)
            if exposure_time_tag in p:
                exposure_time = p[exposure_time_tag].value

            tube_current = ''
            tube_current_tag = (0x18, 0x1151)
            if tube_current_tag in p:
                tube_current = p[tube_current_tag].value

            kvp = ''
            kvp_tag = (0x18, 0x60)
            if kvp_tag in p:
                kvp = p[kvp_tag].value

            slice_thickness = ''
            slice_thickness_tag = (0x18, 0x50)
            if slice_thickness_tag in p:
                slice_thickness = p[slice_thickness_tag].value

            pixel_spacing = ''
            pixel_spacing_tag = (0x28, 0x30)
            if pixel_spacing_tag in p:
                pixel_spacing = p[pixel_spacing_tag].value

            convolution_kernel = ''
            convolution_kernel_tag = (0x18, 0x1210)
            if convolution_kernel_tag in p:
                convolution_kernel = p[convolution_kernel_tag].value

            filter_type = ''
            filter_type_tag = (0x18, 0x1160)
            if filter_type_tag in p:
                filter_type = p[filter_type_tag].value

            patient_position = ''
            patient_position_tag = (0x18, 0x5100)
            if patient_position_tag in p:
                patient_position = p[patient_position_tag].value

            institute_name = get_institute_name(file_path)

            requested_procedure = ''
            requested_procedure_tag = (0x32, 0x1060)
            if requested_procedure_tag in p:
                requested_procedure = p[requested_procedure_tag].value

            line = '{};{};{};{};{};{};{};{};{};{};{};{};{};{}'.format(
                file_path, manufacturer, model_name, software_version, exposure_time, tube_current, kvp,
                slice_thickness, pixel_spacing, convolution_kernel, filter_type, patient_position, institute_name,
                requested_procedure)
            rows.append(line)
            self.poutput(line)

        header = 'file_path;manufacturer;model_name;software_version;exposure_time;tube_current;kvp;slice_thickness;' \
                 'pixel_spacing;convolution_kernel;filter_type;patient_position;institute_name;requested_procedure'
        self.poutput('Writing scan properties to {}'.format(output_file))
        with open(output_file, 'w') as f:
            f.write(header + '\n')
            for row in rows:
                f.write(row + '\n')
        self.poutput('Finished writing')


def main():
    import sys
    shell = DicomExplorerShell()
    sys.exit(shell.cmdloop())


if __name__ == '__main__':
    main()
