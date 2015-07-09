# A python utility that interfaces with some MIDAS programs

import os
import sys
import argparse
import getpass
import midas
import distutils

def main():

    # Initialize the argument parser.
    parser = argparse.ArgumentParser()
    
    # Configure the argument parser.
    parser.add_argument('cmd', nargs='+', help='the primary mhelper command')

    # Parse the command line arguments.
    args = parser.parse_args()

    if args.cmd[0] == 'init':
        init(args.cmd)

    return 0

def init(args):

    if 'help' in args:
        print 'usage: mhelper init [expt-name expt-dir expt-data]'
        sys.exit(0)
    
    print 'Initializing a new MIDAS experiment.'
    print 'Press enter to select default options in brackets.'

    exptlist = midas.ExptList()

    # Deal with optional arguments
    if len(args) > 1:
        expt_name = args[1]
        
    else:
        expt_name = ''
        
    if len(args) > 2:
        expt_dir = args[2]

    else:
        expt_dir = ''

    if len(args) > 3:
        datadir = args[3]

    else:
        datadir = ''

    # Set the experiment name.
    while expt_name == '':

        expt_name = raw_input('Enter a valid name for the experiment: ')

        if expt_name in exptlist.expt_names:
            print '%s is already an existing experiment.' % expt_name
            expt_name = ''
    
    # Set the experiment base directory.
    while expt_dir == '':

        expt_dir = raw_input('Enter expt_dir directory [%s]: ' % os.getcwd())
        expt_dir = os.path.realpath(expt_dir)

        if not os.path.isdir(os.path.split(expt_dir)[0]):
            print 'Invalid directory path.'
            expt_dir = ''

        elif not os.path.isdir(expt_dir):
            s = raw_input('Path does not exist, but parent does. Create? ')
            
            if distutils.util.strtobool(s):
                os.mkdir(expt_dir)

            else:
                expt_dir = ''

        elif expt_dir == '/':
            print 'Cannot set experiment to root directory.'
            expt_dir = ''

    # Get the user name.
    user = getpass.getuser()
        
    print 'Adding experiment to the MIDAS exptab.'
    try:
        with open('exptab', 'a+') as f:
            f.write('%s %s %s\n' % (expt_name, expt_dir, user))

    except:
        print 'Couldn\'t append to /etc/exptab.  You may need to run as sudo.'
        sys.exit(1)
        
    # Check the first one to make sure we have write permissions.
    print 'Creating online directory'
    try:
        os.mkdir(expt_dir + '/online')
        base = expt_dir + '/online/'
    
    except:
        print 'Could not create online directory.  May need to run as sudo'
        sys.exit(1)

    print 'Creating subdirectories: bin, www, frontends'
    os.mkdir(base + 'www')
    os.mkdir(base + 'bin')
    os.mkdir(base + 'frontends')

    print 'Creating resources directory'
    os.mkdir(expt_dir + '/resources')
    base = expt_dir + '/resources/'

    print 'Creating subdirectories: history, logs, elog'
    os.mkdir(base + 'history')
    os.mkdir(base + 'elog')
    os.mkdir(base + 'logs')    
    
    print 'Creating common directory'
    os.mkdir(expt_dir + '/common')
    base = expt_dir + '/common/'

    print 'Creating subdirectories: scripts, code, config'
    os.mkdir(base + 'scripts')    
    os.mkdir(base + 'code')    
    os.mkdir(base + 'config')    

    print 'Creating offline directory'
    os.mkdir(expt_dir + '/offline')            

    # Set up the data directory.
    if datadir == '':
        pass

    elif not os.path.isdir(os.path.split(datadir)[0]):
        print 'Invalid data directory'
        datadir = ''

    elif not os.path.isdir(datadir):
        s = raw_input('Path does not exist, but parent does. Create path?')
        
        if distutils.util.strtobool(s):
            print 'Creating data directory.'
            os.mkdir(datadir)

            print 'Linking data directory [%s] to resources/data'
            os.symlink(datadir, expt_dir + '/resources/data')

        else:
            datadir = ''

    else:
        print 'Linking data directory [%s] to resources/data'
        os.symlink(datadir, expt_dir + '/resources/data')

    tmp = expt_dir + '/resources/data'
    while datadir == '':

        datadir = raw_input('Enter a valid data directory [%s]: ' % tmp)
        try:
            datadir = os.path.realpath(datadir)

        except:
            datadir = os.getcwd() + datadir

        if datadir == '':
            datadir = tmp
    
        if datadir == tmp:
            print 'Creating data directory as resources/data'
            os.mkdir(datadir)

        elif not os.path.isdir(os.path.split(datadir)[0]):
            print 'Invalid data directory'
            datadir = ''

        elif not os.path.isdir(datadir):
            s = raw_input('Path does not exist, parent does. Create path?')
            
            if distutils.util.strtobool(s):
                print 'Creating data directory.'
                os.mkdir(datadir)
                
                print 'Linking data directory [%s] to resources/data' % datadir
                os.symlink(datadir, expt_dir + '/resources/data')

        else:
            print 'Linking data directory [%s] to resources/data' % datadir
            os.symlink(datadir, expt_dir + '/resources/data')

    return 0


if __name__ == '__main__':

    main()
