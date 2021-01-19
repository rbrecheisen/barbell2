import os
import pydicom

from pydicom._dicom_dict import DicomDictionary
from barbell2.lib import BasicShell


class DicomExplorer(BasicShell):

    def __init__(self):
        super(DicomExplorer, self).__init__()
        self.intro = 'Welcome to DICOM Explorer 2!'
        self.prompt = '(dicom) '

    ###

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

    ###

    def do_load_file(self, file_path):
        """ Usage: load_file <file name or path>
        Load a single DICOM file. If only a file name is provided, it's location is assumed to be the
        current directory. Otherwise, the full path must be given.
        """
        if not os.path.isfile(file_path):
            file_path = os.path.join(self.current_dir, file_path)
        if not self.is_dicom(file_path):
            self.poutput('File is not DICOM')
            return
        self.poutput('Loading file...')
        self.add_result(file_path, desc='Single file')
        self.poutput('Ok')

    def do_load_dir(self, dir_path):
        """ Usage: load_dir <dir name or path>
        Load (recursively) all DICOM files in the given directory. If only the directory name is given, it is
        assumed that the directory is located in the current directory. Otherwise, the full path must be given.
        """
        if not os.path.isdir(dir_path):
            dir_path = os.path.join(self.current_dir, dir_path)
        self.poutput('Loading {}...'.format(dir_path))
        data = []
        for root, dirs, files in os.walk(dir_path):
            for f in files:
                if not f.startswith('._'):
                    f = os.path.join(root, f)
                    if self.is_dicom(f):
                        data.append(f)
                        self.poutput(f)
        self.add_result(data, desc='Files ({})'.format(len(data)))
        self.poutput('Loaded {} files'.format(len(data)))
        self.poutput('Ok')

    def do_show_files(self, n):
        """ Usage: show_files [n]
        Show files loaded in the current result set. If you want to show files from another result set
        select it first using the set_current_result command. If you specify n > 0, the first n files
        will be displayed. If you specify n < 0, the last n files will be displayed.
        """
        files = self.results[self.current_key]['data']
        try:
            n = 0 if n == '' else int(n)
        except ValueError as e:
            self.poutput(e)
        if n == 0:
            for f in files:
                self.poutput(f)
        elif n > 0:
            n = n if n < len(files) else len(files) - 1
            for i in range(n):
                self.poutput(files[i])
        elif n < 0:
            n = -n
            n = n if n < len(files) else len(files) - 1
            for i in range(len(files) - n, len(files)):
                self.poutput(files[i])
        else:
            self.poutput('Illegal n = {}'.format(n))
        self.poutput('Ok')

    def do_lookup_tag(self, tag_name):
        """ Usage: lookup_tag <tag name>
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
        self.poutput('Ok')

    def do_show_tags(self, tag_name):
        """ Usage: show_tag <tag name>
        Show values for tag <tag name> in the currently loaded DICOM files.
        """
        files = self.results[self.current_key]['data']
        tag = self.tag_for_name(tag_name)
        self.poutput(tag)
        for f in files:
            p = pydicom.read_file(f)
            if tag in list(p.keys()):
                self.poutput('{}: {}'.format(f, p[tag].value))
        self.poutput('Ok')

    def do_dump(self, file_path):
        """ Usage: dump file_path
        Dumps DICOM header for file <file_path>. If the file path does not exist, it must be only a file name
        and a search is done in the current result set files. If only one hit is found, its header will be
        dumped. If multiple hits have been found, a list of these file paths is shown from which the user
        must choose.
        """
        files = self.results[self.current_key]['data']
        if not os.path.isfile(file_path):
            hits = []
            for f in files:
                if file_path in f:
                    hits.append(f)
            if len(hits) == 1:
                p = pydicom.read_file(file_path)
                self.poutput(p)
            else:
                self.poutput('Choose one of the following candidates:')
                for hit in hits:
                    self.poutput(hit)
        else:
            p = pydicom.read_file(file_path)
            self.poutput(p)
        self.poutput('Ok')

    def do_check_pixels(self, verbose):
        files = self.results[self.current_key]['data']
        bad_files = []
        for f in files:
            p = pydicom.read_file(f)
            try:
                p.convert_pixel_data()
                if verbose != '':
                    self.poutput('OK: {}'.format(f))
            except NotImplementedError:
                bad_files.append(f)
        if len(bad_files) > 0:
            for f in bad_files:
                self.poutput('ERROR: {}'.format(f))
            self.add_result(bad_files, desc='Files with compressed pixels ({})'.format(len(bad_files)))
            self.do_show_results(None)
        self.poutput('Ok')

    def do_to_raw(self, output_dir):
        result = os.system('which gdcmconv>/dev/null')
        if result > 0:
            self.poutput('Tool gdcmconv is not installed')
            return
        os.makedirs(output_dir, exist_ok=False)
        files = self.results[self.current_key]['data']
        for f in files:
            target_file = os.path.join(output_dir, os.path.split(f)[1])
            command = 'gdcmconv --raw {} {}'.format(f, target_file)
            os.system(command)
            self.poutput('Converted {}'.format(f))


def main():
    import sys
    shell = DicomExplorer()
    sys.exit(shell.cmdloop())


if __name__ == '__main__':
    main()
