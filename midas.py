# A simple python wrapper around odb calls to make initialization easier

import os
from subprocess import call, Popen, PIPE

class Expt:
    def __init__(self, expname=None):

        if expname is None:
            self.expname = Exptab().current_expt()
        else:
            self.expname = expname

        with open(os.environ['MIDAS_EXPTAB']) as f:
            exptab = f.read().split('\n')
            for line in exptab:
                if line.split(' ')[0] == self.expname:
                    midasdir = line.split(' ')[1]
                    self.expdir = midasdir.replace('/resources', '')

    def start(self, modules=None):
        
        if modules is None:
            script = '%s/online/bin/start_daq.sh' % self.expdir
            print script
            call(script)

        else:
            for m in modules:

                if m == 'frontends':
                    script = '%s/online/bin/start_frontends.sh' % self.expdir
                    call(script)
        
                elif m == 'analyzers':
                    script = '%s/online/bin/start_analyzers.sh' % self.expdir
                    call(script)

                elif m == 'midas':
                    script = '%s/online/bin/start_midas.sh' % self.expdir
                    call(script)
                
                else:
                    print "Not a valid set of modules."


    def kill(self, modules=None):
        
        if modules is None:
            script = '%s/online/bin/kill_daq.sh' % self.expdir
            call(script)

        else:
            for m in modules:

                if m == 'frontends':
                    script = '%s/online/bin/kill_frontends.sh' % self.expdir
                    call(script)
        
                elif m == 'analyzers':
                    script = '%s/online/bin/kill_analyzers.sh' % self.expdir
                    call(script)

                elif m == 'midas':
                    script = '%s/online/bin/kill_midas.sh' % self.expdir
                    call(script)
                
                else:
                    print "Not a valid set of modules."

    def restart(self, modules=None):

        self.kill(modules)
        self.start(modules)


class ODB:
    def __init__(self, expname=None):
        self.expname = expname
        with open(os.environ['MIDAS_EXPTAB']) as f:
            exptab = f.read().split('\n')
            for line in exptab:
                if line.find(self.expname) != -1:
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

    def get_value(self, key):
        cmd = ['odbedit', '-e', self.expname, '-c']
        cmd.append('ls -v "' + key + '"')
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        return output

    def set_value(self, key, val):
        cmd = ['odbedit', '-e', self.expname, '-c']
        cmd.append('set "' + key + '" "' + str(val) + '"')
        return call(cmd)

    def call_cmd(self, cmdstring):
        cmd = ['odbedit', '-e', self.expname, '-c']
        cmd.append(cmdstring)
        return call(cmd)

    def add_entry(self, entry):
        entry_path = entry.keys()[0]
        entry_type = entry[entry_path]['type'].lower()
        entry_data = entry[entry_path]['value']

        if entry_type == "path":
            if self.expdir[-1] == '/':
                entry_data = self.expdir + entry_data
            else:
                entry_data = self.expdir + '/' + entry_data
                
            self.call_cmd('create string "%s[1][256]"' % entry_path)
            self.call_cmd('set "%s" "%s"' % (entry_path, entry_data))

        else:
            self.call_cmd('create "%s" "%s"' % (entry_type, entry_path))
            self.call_cmd('set "%s" "%s"' % (entry_path, entry_data))


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
    
    
