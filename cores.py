#!/usr/bin/env python

# Copyright (C) 2017-2022 Greenweaves Software Limited

# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>

# snarfed from http://stackoverflow.com/questions/19086106/how-to-utilize-all-cores-with-python-multiprocessing

#
# Execute leighton.py on multiple cores.
#
# Do not try to run this under the IDE, as it fights with multiprocessing!

# For an explanation, see https://docs.python.org/3.5/library/multiprocessing.html, which warns
#    Functionality within this package requires that the __main__ module be importable by the children.
#    This is covered in Programming guidelines however it is worth pointing out here.
#    This means that some examples, such as the multiprocessing.pool.Pool examples will not work
#    in the interactive interpreter.

from getopt          import getopt, GetoptError
from leighton        import main
from multiprocessing import current_process, Manager, Pool
from os              import environ
from sys             import argv, exit
from time            import time


def init_worker(mps, fps, cut):
    ''' This will be called by each process when it starts'''
    global memorizedPaths, filepaths, cutoff
    global DG

    print ('process initializing', current_process())
    memorizedPaths, filepaths, cutoff = mps, fps, cut
    DG                                = 1


def work(item):
    ''' Used to execute the model once for each'''
    print ('Processing {0}'.format(item))
    main(item.split())

def help():
    print ('python cores.py datafile')

def parse_command_line(argv):
    input_file  = 'cores.dat'
    if len(argv[1:])>0:
        try:
            opts, args = getopt(argv[1:],'',[])
            for opt, arg in opts:
                pass
            input_file = args[0]
        except GetoptError:
            help()
            exit(2)
    return input_file

if __name__ == '__main__':

    if 'WINGDB_ACTIVE' not in environ.keys(): # Detect whether running under IDE or command line
        start_time     = time()
        manager        = Manager()
        memorizedPaths = manager.dict()
        filepaths      = manager.dict()
        cutoff         = 1
        pool           = Pool(initializer = init_worker,   # Create process pool to use all available CPUs
                              initargs    = (memorizedPaths, filepaths, cutoff))
        input_file     = parse_command_line(argv[1:])
        print ('Opening {0}'.format(input_file))
        with open(input_file) as file:
            for _ in pool.imap_unordered(work,
                                         [line.strip() for line in  file.readlines() if len(line.strip())>0],
                                         chunksize=1):
                pass

            pool.close()
            pool.join()
            print('--- %s seconds ---' % (time() - start_time))
    else:
        print ('cores.py must be executed from command line, not from IDE')
