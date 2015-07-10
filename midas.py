# A simple python wrapper around odb calls to make initialization easier

import os
from subprocess import call

class ODB:
    def __init__(self, expname):
        self.expname = expname
        with open(os.environ['MIDAS_EXPTAB']) as f:
            exptab = f.read().split('\n')
            for line in exptab:
                if line.find(expname) != -1:
                    midasdir = line.split(' ')[1]
                    self.expdir = midasdir.replace('/resources', '')

    def mkdir(self, dirname):
        cmd = ['odbedit', '-e', self.expname, '-c']
        cmd.append('mkdir "' + dirname + '"')
        return call(cmd)

    def create_key(self, path, typestring, key):
        cmd = ['odbedit', '-e', self.expname, '-c']
        cmd.append('create ' + typestring + ' "' + path + '/' + str(key) + '"')
        return call(cmd)

    def set_value(self, key, val):
        cmd = ['odbedit', '-e', self.expname, '-c']
        cmd.append('set "' + key + '" "' + str(val) + '"')
        return call(cmd)

    def call_cmd(self, cmdstring):
        cmd = ['odbedit', '-e', self.expname, '-c']
        cmd.append(cmdstring)
        return call(cmd)

class Exptab:
    def __init__(self, exptab='/etc/exptab'):
        self.exptab = exptab
        self.expt_names = []
        self.expt_dirs = []

        with open('/etc/exptab', 'r') as f:
            
            lines = f.read()
            lines = lines.split('\n')
            
            for line in lines:

                if line == '':
                    continue

                self.expt_names.append(line.split(' ')[0])
                self.expt_dirs.append(os.path.split(line.split(' ')[1])[0])


    # A function that determines the experiment currently being worked on.
    def current_expt(self):

        # getcwd routes symlinks to their absolute path, and that's not
        # what we want. PWD isn't portable however.
        try:
            cwd = os.environ['PWD']

        except:
            cwd = os.getcwd()
            
        expt_list_string = 'Current experiments:\n'

        # Match against experiment base directories.
        for i in range(len(self.expt_dirs)):
            
            expt_list_string += '    %s [%i]\n' % (self.expt_names[i], i)
            if cwd.startswith(self.expt_dirs[i]):
                return self.expt_names[i]

        # If we made it here we don't know.
    
        while True:
            expt_num = raw_input(expt_list_string + 'Choose experiment: ')

            try:
                expname = self.expt_names[int(expt_num)]
                break

            except:
                print 'Not a valid experiment number.'

        return expname

    def current_expt_dir(self):
        
        expt_name = self.current_expt()
        return self.get_expt_dir(expt_name)


    def get_expt_dir(self, expt_name):
        
        for i in range(len(self.expt_names)):

            if expt_name == self.expt_names[i]:
                return self.expt_dirs[i]

        print 'Could not find experiment.'
        return None

def launch_frontend(fe_path):
    
    expt = Exptab().current_expt()

    fe_name = os.path.split(fe_path)[1].replace('_', '-')
    sc_name = '%s.%s' % (expt, fe_name)

    # Create the screen first.
    cmd = ['screen', '-dmS', sc_name]
    call(cmd)

    # Now send the command to run the frontend.
    cmd = ['screen', '-S', sc_name, '-p', '0', '-rX', 'stuff']
    cmd.append('"%s -e %s$(printf \\\\r)"' % (fe_path, expt))
    call(' '.join(cmd), shell=True)
    
    
