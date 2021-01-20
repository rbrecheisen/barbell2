import os
import cmd2


INTRO = """
Welcome to BasicShell!
======================
Please extend this class to create your own interactive shell applications.
Type 'help' to view the commands available in BasicShell.
"""

PROMPT = '(shell) '


class BasicShell(cmd2.Cmd):

    def __init__(self):
        super(BasicShell, self).__init__()
        self.debug = True
        self.intro = INTRO
        self.prompt = PROMPT
        self.current_dir = os.path.abspath(os.path.curdir)
        self.idx = -1
        self.results = {}
        self.current_key = None
        self.last_idx = self.idx

    def next_idx(self):
        self.idx += 1
        self.last_idx = self.idx
        return self.idx

    def add_result(self, data, desc=None):
        key = 'result_{}'.format(self.next_idx())
        self.results[key] = {'data': data, 'desc': desc}
        self.current_key = key

    ###

    def do_show_results(self, _=None):
        for k in self.results.keys():
            current = ''
            if k == self.current_key:
                current = '** current **'
            self.poutput('{}: {} {}'.format(k, self.results[k]['desc'], current))

    def do_set_result_data(self, line):
        items = [x.strip() for x in line.split('=')]
        self.results[items[0]]['data'] = items[1]

    def do_set_result_desc(self, line):
        items = [x.strip() for x in line.split('=')]
        self.results[items[0]]['desc'] = items[1]

    def do_set_current_key(self, key):
        self.current_key = key

    ###

    def do_cd(self, line):
        """ Usage: cd <dir path>
        Change the current directory to <dir path>
        """
        if line == '.' or line == '':
            self.do_pwd(None)
            return
        if line == '..':
            self.current_dir = os.path.split(self.current_dir)[0]
            self.do_pwd(None)
            return
        if not os.path.isdir(line):
            line = os.path.join(self.current_dir, line)
            if not os.path.isdir(line):
                self.poutput('Directory {} is not a valid directory'.format(line))
                return
        self.current_dir = line
        self.do_pwd(None)

    def do_ls(self, _=None):
        """ Usage: ls
        Lists the contents of the current directory. Same as shell command "!ls -lap".
        """
        self.do_shell('cd {}; ls -lap'.format(self.current_dir))

    def do_shell(self, line):
        """ Usage: !<command>
        Execute shell command <command>. For example, !echo $HOME will display the user's HOME directory.
        """
        if line is None or line is '':
            self.poutput('Please specify a shell command preceded by! For example, !echo $HOME')
        else:
            self.poutput('Running shell command: {}'.format(line))
            output = os.popen(line).read()
            self.poutput(output)

    def do_pwd(self, _=None):
        """ Usage: pwd
        Show the current directory.
        """
        self.poutput(self.current_dir)

    def do_undo(self, verbose=None):
        """ Usage: undo
        Move to the previous result set (if any).
        """
        idx = int(self.current_key.split('_')[1]) - 1
        idx = 0 if idx < 0 else idx
        self.idx = idx
        self.current_key = 'result_{}'.format(self.idx)
        if verbose:
            self.do_show_results(None)

    def do_redo(self, verbose=None):
        """ Usage: redo
        Move to the next result set (if any).
        """
        idx = int(self.current_key.split('_')[1]) + 1
        idx = self.last_idx if idx > self.last_idx else idx
        self.idx = idx
        self.current_key = 'result_{}'.format(self.idx)
        if verbose:
            self.do_show_results(None)

    @staticmethod
    def do_exit(_=None):
        """ Usage: exit
        Quits the shell application (same as quit).
        """
        return True


def main():
    import sys
    shell = BasicShell()
    sys.exit(shell.cmdloop())


if __name__ == '__main__':
    main()
