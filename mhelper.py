# A python utility that interfaces with some MIDAS programs

import argparse
import os
import sys

def main():

    # Initialize the argument parser.
    parser = argparse.ArgumentParser()
    
    # Configure the argument parser.
    parser.add_argument('cmd', help='the primary mhelper command')
    parser.add_argument('-e' ,'--expt', help='experiment name')

    # Parse the command line arguments.
    args = parser.parse_args()

    if args.cmd == 'init':
        init()

    return 0

def init():

    print 'Creating a new MIDAS experiment'
    print 'Press enter to select the default option in brackets.'
    wd = raw_input('Enter base directory [%s]' % os.path.getpwd())
    print wd
    
    return 0


if __name__ == '__main__':
    main()
