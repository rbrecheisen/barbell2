import os
import pydicom

from pydicom._dicom_dict import DicomDictionary


class DicomExplorer:

    def __init__(self):
        super(DicomExplorer, self).__init__()
        self.files = []

    @staticmethod
    def is_dicom(file_path):
        if not os.path.isfile(file_path):
            return False
        try:
            with open(file_path, "rb") as f:
                return f.read(132).decode("ASCII")[-4:] == "DICM"
        except UnicodeDecodeError:
            return False

    @staticmethod
    def tag_for_name(name):
        for key, value in DicomDictionary.items():
            if name == value[4]:
                return hex(int(key))

    def load_file(self, file_path):
        """ Usage: load_file <file name or path>
        Load a single DICOM file. If only a file name is provided, it's location is assumed to be the
        current directory. Otherwise, the full path must be given.
        """
        if not os.path.isfile(file_path):
            print('Cannot find file {}'.format(file_path))
            return
        if not self.is_dicom(file_path):
            print('File is not DICOM')
            return
        print('Loading file...')
        self.files.append(file_path)
        # self.add_result(file_path, desc='Single file')
        print('Ok')

    def load_dir(self, dir_path):
        """ Usage: load_dir <dir name or path>
        Load (recursively) all DICOM files in the given directory. If only the directory name is given, it is
        assumed that the directory is located in the current directory. Otherwise, the full path must be given.
        """
        if not os.path.isdir(dir_path):
            print('Cannot find directory {}'.format(dir_path))
            return
        print('Loading {}...'.format(dir_path))
        for root, dirs, files in os.walk(dir_path):
            for f in files:
                if not f.startswith('._'):
                    f = os.path.join(root, f)
                    if self.is_dicom(f):
                        self.files.append(f)
                        print(f)
        print('Loaded {} files'.format(len(data)))
        print('Ok')

    def show_files(self, n):
        """ Usage: show_files [n]
        Show files loaded in the current result set. If you want to show files from another result set
        select it first using the set_current_result command. If you specify n > 0, the first n files
        will be displayed. If you specify n < 0, the last n files will be displayed.
        """
        files = self.files
        try:
            n = 0 if n == '' else int(n)
        except ValueError as e:
            print(e)
        if n == 0:
            for f in files:
                print(f)
        elif n > 0:
            n = n if n < len(files) else len(files) - 1
            for i in range(n):
                print(files[i])
        elif n < 0:
            n = -n
            n = n if n < len(files) else len(files) - 1
            for i in range(len(files) - n, len(files)):
                print(files[i])
        else:
            print('Illegal n = {}'.format(n))
        print('Ok')

    def lookup_tag(self, tag_name):
        """ Usage: lookup_tag <tag name>
        Lookup tag <tag name> in the DICOM dictionary. You can specify only parts of a tag name, e.g.,
        "Transmit" will return multiple dictionary entries containing the word "Transmit" (like Transmit
        Coil Name). Being able to lookup tags comes in handy when you search for them in DICOM files.
        Note that (parts of) the tag name does not have to be case-sensitive.
        """
        for key, value in DicomDictionary.items():
            output = '{}: {}'.format(key, value)
            if tag_name == '':
                print(output)
            else:
                for item in value:
                    if tag_name in item:
                        print(output)
        print('Ok')

    def show_values(self, tag_name):
        """ Usage: show_values <tag name>
        Show values for tag <tag name> in the currently loaded DICOM files.
        """
        files = self.files
        tag = self.tag_for_name(tag_name)
        print(tag)
        for f in files:
            p = pydicom.read_file(f)
            if tag in list(p.keys()):
                print('{}: {}'.format(f, p[tag].value))
        print('Ok')

    def dump(self, file_path):
        """ Usage: dump file_path
        Dumps DICOM header for file <file_path>. If the file path does not exist, it must be only a file name
        and a search is done in the current result set files. If only one hit is found, its header will be
        dumped. If multiple hits have been found, a list of these file paths is shown from which the user
        must choose.
        """
        if os.path.isfile(file_path):
            p = pydicom.read_file(file_path)
            print(p)
        else:
            files = self.files
            hits = []
            for f in files:
                if file_path in f:
                    hits.append(f)
            if len(hits) == 0:
                print('File {} not found'.format(file_path))
            elif len(hits) == 1:
                p = pydicom.read_file(file_path)
                print(p)
            else:
                print('Choose one of the following candidates:')
                for hit in hits:
                    print(hit)
        print('Ok')

    def check_pixels(self, verbose):
        """ Usage: check_pixels
        Checks for each file in the current result set whether its pixels can be loaded using the pydicom
        package. If not, this may be caused by the fact that the pixel values are compressed, e.g., in
        JPEG2000 format. To uncompress the values, use the 'to_raw' command of this tool.
        """
        files = self.files
        bad_files = []
        for f in files:
            p = pydicom.read_file(f)
            try:
                p.convert_pixel_data()
                if verbose != '':
                    print('OK: {}'.format(f))
            except NotImplementedError:
                bad_files.append(f)
        if len(bad_files) > 0:
            for f in bad_files:
                print('ERROR: {}'.format(f))
        print('Ok')

    def to_raw(self, output_dir):
        """ Usage: to_raw <output_dir>
        Decompress pixel values to raw format in case they have been compressed. This command requires that
        the tool gdcmconv is installed. To install it using HomeBrew (for Mac). The command requires an empty
        output directory where the converted DICOMs are saved.
        """
        result = os.system('which gdcmconv>/dev/null')
        if result > 0:
            print('Tool gdcmconv is not installed')
            return
        os.makedirs(output_dir, exist_ok=False)
        files = self.files
        for f in files:
            target_file = os.path.join(output_dir, os.path.split(f)[1])
            command = 'gdcmconv --raw {} {}'.format(f, target_file)
            os.system(command)
            print('Converted {}'.format(f))


def main():
    pass


if __name__ == '__main__':
    main()
