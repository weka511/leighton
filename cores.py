# Copyright (C) 2017-2019 Greenweaves Software Limited

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

import multiprocessing as mp, leighton, time, getopt,sys

# This will be called by each process when it starts

def init_worker(mps, fps, cut):
    global memorizedPaths, filepaths, cutoff
    global DG

    print ('process initializing', mp.current_process())
    memorizedPaths, filepaths, cutoff = mps, fps, cut
    DG                                = 1

# Used to execute the model once for each 
def work(item):
    print ('Processing {0}'.format(item))
    leighton.main(item.split())

def help():
    print ('python cores.py datafile')
    
def parse_command_line(argv):
    input_file  = 'cores.dat'
    if len(sys.argv[1:])>0:
        try:
            opts, args = getopt.getopt(sys.argv[1:],'',[])
            for opt, arg in opts: 
                pass
            input_file = args[0]
        except getopt.GetoptError:
            help()
            sys.exit(2)
    return input_file

if __name__ == '__main__':
    # Detect whether running undrt IDE or command line - 
    # see https://stackoverflow.com/questions/552627/python-ide-vs-cmd-line-detection
    if sys.stdin.isatty():
        start_time     = time.time() 
        manager        = mp.Manager()
        memorizedPaths = manager.dict()
        filepaths      = manager.dict()
        cutoff         = 1
    
        # Create process pool to use all available CPUs
        pool           = mp.Pool(initializer=init_worker, initargs=(memorizedPaths, filepaths, cutoff))
        input_file     = parse_command_line(sys.argv[1:])
        print ('Opening {0}'.format(input_file))
        with open(input_file) as file:
            for _ in pool.imap_unordered(work,
                                         [line.strip() for line in  file.readlines() if len(line.strip())>0],
                                         chunksize=1):
                pass
            
            pool.close()
            pool.join()
            print('--- %s seconds ---' % (time.time() - start_time))            
    else:
        print ("cores.py must be executed from command line, not from IDE")