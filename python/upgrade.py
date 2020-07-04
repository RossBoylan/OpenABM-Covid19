#! /usr/bin/env python3
# previous line is python virtual environment friendly

# File: upgrade.py
# Author: Ross Boylan <ross.boylan@ucsf.edu>
# Created: 2020-07-03
#
# Detect and correct local parameter files built with
# a different parameter list than current.

import argparse
import pandas as pd
from pathlib import Path
import sys

apd = """Scans old parameter files and checks for compatiblity with the 
current OpenABM-Covid19 requirements.  Optionally, update those files to
match the current requirements."""
ape="""--rename or --override, which may be combined, imply --update.
If you request update of foo.csv it will be left as foo.bak when you are done.

Specify file arguments before all options, or use -- to separate files from options.

Note that override and rename take arguments separated by spaces, not commas."""
parser = argparse.ArgumentParser(description=apd, epilog=ape)
parser.add_argument('files', nargs='+',
                    help="old files with parameters (csv). Shell globbing permitted.")
parser.add_argument('--valcheck', action='store_true',
                    help = "check that parameter values, as well as names, match")
parser.add_argument('--update', action='store_true',
                    help = "Change the files to match new scheme")
parser.add_argument('--override', nargs='+',
                    help="parameters for which you will specify the  value. Python regular expressions allowed")
parser.add_argument('--rename', nargs='+',
                    help="names of variables in new scheme that you will create by renaming old ones. Regex permitted.")
parser.add_argument('--newbaseline', default="tests/data/baseline_parameters.csv",
                    type=Path,
                    help="location of file with the new parameter schema")
# -- is to distinguish files from other arguments if necessary
# easier just to specify the file arguments first.
parser.add_argument('--', help=argparse.SUPPRESS, dest="dontcare", )

myargs = parser.parse_args()
if myargs.override or myargs.rename:
    myargs.update = True


def locate_top(path : Path) -> Path:
    """Return a <Path> that is my best guess for installation location
    The main reason to bother with this is to allow the program to be invoked from
    other locations.  Secondarily, it allows relative specification of newbaseline.

    If upgrade.py itself is moved to another location, or possibly invoked through
    a symlink at another location, there will likely be no joy.
    """
    path = path.resolve()
    adir = path # not a dir now, but will be
    while len(adir.parts) > 2:
        adir = adir.parent
        if adir.name.upper() == "OPENABM-COVID19":
            return adir
    # no luck.  guess parent of where this file is found
    return path.parent

def go_file(master : pd.DataFrame, theOld : Path):
    """Compare theOld to the values in master.
    If requested, update the old file"""
    olddf = pd.read_csv(theOld)
    old = set(olddf.columns)
    new = set(master.columns)
    justnew = new - old
    justold = old - new
    if justnew or justold:
        # we have some differences
        print("{} is not consistent with current parameters.\n".format(theOld.name))
        if justnew:
            print("\tOnly in the new scheme: {}".format(justnew))
        if justold:
            print("\tOnly in the old scheme: {}".format(justold))
    else:
        print("{} names match new scheme.".format(theOld.name))
    # a lot more to go
    
def go_glob(master : pd.DataFrame, theGlob : str):
    """theGlob is either a file path or a glob that yields them.
    Get the individual files and process each one."""
    for f in Path(".").glob(theGlob):
        go_file(master, f)
        
def go():
    template = locate_top(Path(sys.argv[0])) / myargs.newbaseline
    master = pd.read_csv(template)
    for fglob in myargs.files:
        go_glob(master, fglob)
    breakpoint()
    print(master)

if __name__ == "__main__":
    go()

