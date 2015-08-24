# A python utility that interfaces with some MIDAS programs

import os
import sys
import argparse
import getpass
import distutils
import git
import simplejson
from difflib import SequenceMatcher
import operator

import midas

def main():

    # Initialize the argument parser.
    parser = argparse.ArgumentParser()
    
    # Configure the argument parser.
    parser.add_argument('cmd', nargs='+', 
        help='init, link, expt, resource, add-to-odb, search-runlog')

    # Parse the command line arguments.
    args = parser.parse_args()

    if args.cmd[0] == 'init':
        init(args.cmd)

    elif args.cmd[0] == 'link':
        link(args.cmd)

    elif args.cmd[0] == 'expt':
        print midas.Exptab().current_expt()

    elif args.cmd[0] == 'daq':
        daq_control(args.cmd)

    elif args.cmd[0] == 'resource':
        resource(args.cmd)

    elif args.cmd[0] == 'add-to-odb':
        add_to_odb(args.cmd)

    elif args.cmd[0] == 'search-runlog':
        search_runlog(args.cmd)

    else:
        print parser.print_help()

    return 0


def init(args):

    if 'help' in args:
        print 'usage: mhelper init [expt-name expt-dir expt-data]'
        sys.exit(0)
    
    print 'Initializing a new MIDAS experiment.'
    print 'Press enter to select default options in brackets.'

    exptlist = midas.Exptab()

    # Deal with optional arguments
    if len(args) > 1:
        expt_name = args[1]
        
    else:
        expt_name = ''
        
    if len(args) > 2:
        expt_dir = os.path.realpath(args[2])

    else:
        expt_dir = ''

    if len(args) > 3:
        datadir = os.path.realpath(args[3])

    else:
        datadir = ''

    # Set the experiment name.
    while (expt_name == '') or (expt_name in exptlist.expt_names):

        expt_name = raw_input('Enter a valid name for the experiment: ')

        if expt_name in exptlist.expt_names:
            print '%s is already an existing experiment.' % expt_name

    print 'Experiment name set to %s.' % expt_name
    
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

    print 'Experiment directory set to %s.' % expt_dir

    # Get the user name.
    user = getpass.getuser()
        
    print 'Adding experiment to the MIDAS exptab.'
    try:
        with open('/etc/exptab', 'a+') as f:
            f.write('%s %s/resources %s\n' % (expt_name, expt_dir, user))

    except:
        print 'Couldn\'t append to /etc/exptab.  Check the permissions.'
        sys.exit(1)
        
    # Check the first one to make sure we have write permissions.
    print 'Creating online directory'
    try:
        os.mkdir(expt_dir + '/online')
        base = expt_dir + '/online/'
    
    except:
        print 'Could not create online directory.  Check your permissions.'
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
        s = raw_input('Path does not exist, but parent does. Create? ')
        
        if distutils.util.strtobool(s):
            print 'Creating data directory.'
            os.mkdir(datadir)

            print 'Linking data directory [%s] to resources/data' % datadir
            os.symlink(datadir, expt_dir + '/resources/data')

        else:
            datadir = ''

    else:
        print 'Linking data directory [%s] to resources/data' % datadir
        os.symlink(datadir, expt_dir + '/resources/data')

    tmp = expt_dir + '/resources/data'
    while datadir == '':

        datadir = raw_input('Enter a valid data directory [%s]: ' % tmp)

        if datadir == '':
            datadir = tmp

        try:
            datadir = os.path.realpath(datadir)

        except:
            datadir = os.getcwd() + datadir
    
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

    print 'Initializing git version control.'
    g = git.cmd.Git(expt_dir)
    g.init()
    
    print 'Setting up .gitignore defaults.'
    with open(expt_dir + '/.gitignore', 'a+') as f:
        f.write('*.o\n')
        f.write('*~\n')
        f.write('*#*\n')
        f.write('*.so\n')
        f.write('*.c*.d\n')
        f.write('\n')
        f.write('resources')

    print 'Adding items for initial commit. It\'s all yours now.'
    g.add('.')

    return 0

# Link something from the resources directory to the current one.
def link(args):

    if len(args) < 2:
        print 'usage: mhelper link <target-dir> [link-dir]'
        return -1

    target_dir = args[1]

    if len(args) > 2:
        link_dir = args[2]

    else:
        link_dir = os.path.split(target_dir)[1]

    # Get the directory for the current experiment
    expt_dir = midas.Exptab().current_expt_dir()

    if target_dir in os.listdir(expt_dir + '/resources'):
        
        path = os.path.realpath(expt_dir + '/resources/' + target_dir)
        os.symlink(path, link_dir)
        return 0
        
    else:
        print 'Target directory was not found in experiment resources.'
        return -1


# Create a new resource directory for the experiment
def resource(args):

    # Get the directory for the current experiment
    expt_dir = midas.Exptab().current_expt_dir()
    
    if len(args) < 2:
        print 'usage: mhelper resource resource-name'
        print 'No resource-name specified.'

    else:
        resource_dir = expt_dir + '/resources/' + args[1]

    if len(args) > 2:
        link_dir = os.path.realpath(args[2])

    else:
        link_dir = ''

    if os.path.isfile(resource_dir):
        print 'A file already exists with the specfied name!'
        return -1

    if os.path.isdir(resource_dir):
        print 'A directory already exists with the specfied name!'
        return -1

    if not os.path.isdir(link_dir):
        print 'Link path is not a directory. Cannot create resource.'
        return -1

    if link_dir == '':
        os.mkdir(resource_dir)
        return 0

    else:
        os.symlink(link_dir, resource_dir)


def add_to_odb(args):
    """Add a set of entries from json or a single entry from the command
    line to the odb"""

    if len(args) < 3:
        
        odb_entries = simplejson.loads(open(args[1]).read())

    else:

        odb_entries = {args[1]: {"type": args[2], "value": args[3]}}

    # Get the ODB object.
    odb = midas.ODB(midas.Exptab().current_expt())
    
    for key in odb_entries.keys():
        odb.add_entry({key: odb_entries[key]})

def daq_control(args):

    if args[1] == 'start':

        if len(args) > 2:
            midas.Expt().start(args[1:])

        else:
            midas.Expt().start()
    
    elif args[1] == 'kill':
        
        if len(args) > 2:
            midas.Expt().kill(args[1:])

        else:
            midas.Expt().kill()

    elif args[1] == 'restart':
        
        if len(args) > 2:
            midas.Expt().restart(args[1:])

        else:
            midas.Expt().restart()

    else:
        print "Not a recognized option for run control [start, stop, restart]."


def search_runlog(args):
    """The function searches the runlog for the best match."""
 
    # Get the runlog as json."
    runlog_file = midas.Exptab().current_expt_dir()
    runlog_file += '/resources/log/runlog.json'
    runlog = simplejson.loads(open(runlog_file).read())

    query = args[1]

    results = {}

    for run in runlog.keys():
        
        comment = runlog[run]['comment']
        ntags = len(runlog[run]['tags']) * 1.0

        results[run] = SequenceMatcher(None, query, comment).ratio()

        for tag in runlog[run]['tags']:
            results[run] += SequenceMatcher(None, query, tag).ratio() / ntags

    sorted_runlog = sorted(results.items(), 
                           key=operator.itemgetter(1), 
                           reverse=True)

    print "Search results on runlog.json"
    for idx, run in enumerate(sorted_runlog):

        text = [runlog[run[0]]['comment']]
        for tag in runlog[run[0]]['tags']:
            text.append(tag)

        print "%i\t%s - (%s)" % (idx + 1, run[0], ', '.join(text))
        

if __name__ == '__main__':

    main()
