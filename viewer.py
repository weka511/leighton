#!/usr/bin/env python

# Copyright (C) 2015-2022 Greenweaves Software Pty Ltd

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

'''Display Martian temperature data'''

from getopt            import getopt, GetoptError
from glob              import glob
from matplotlib.pyplot import figure, show
from os.path           import splitext
from re                import match
from sys               import argv, exit
from utilities         import ExternalTemperatureLog, format_latitude, get_colour


def help():
      print ('viewer.py -i <outputfile>')



def display(inputfile,fignum=1):
      with open(inputfile, 'r') as f:
            history = ExternalTemperatureLog(f)
            fig   = figure(fignum,figsize=(6,6))
            ax    = fig.add_subplot(1,1,1)
            x,y1  = history.extract(1)
            _,y2  = history.extract(2)
            _,y3  = history.extract(3)
            _,y4  = history.extract(4)
            _,y5  = history.extract(5)
            _,y10 = history.extract(10)
            _,y20 = history.extract(20)
            ax.set_title('Diurnal variation in temperature for {0}'.format(inputfile))
            ax.set_xlabel('Time')
            ax.set_ylabel('Temperature - Kelvin')
            ax.grid(True)
            ax.plot(x,y1,'r-',x,y2,'g-',x,y3,'b-',x,y4,'c-',x,y5,'m-',x,y10,'y-',x,y20,'k-')
            fig.savefig(splitext(inputfile)[0]+'-all')

def display_maxmin(inputfile,fignum):
      with open(inputfile, 'r') as f:
            history = ExternalTemperatureLog(f)
            (xxx,ymin,ymax)=history.get_max_min(1)
            fig = figure(fignum,figsize=(6,6))
            ax = fig.add_subplot(1,1,1)
            ax.set_title('Diurnal variation in temperature for {0}'.format(inputfile))
            ax.set_xlabel('Time')
            ax.set_ylabel('Temperature - Kelvin')
            ax.grid(True)
            ax.plot(xxx,ymin,'b-',xxx,ymax,'r-')
            fig.savefig(splitext(inputfile)[0]+'-minmax')


def display_daily_minima(inputfile,fignum,colour,style):
      with open(inputfile, 'r') as f:
            history         = ExternalTemperatureLog(f)
            latitude        = history.get('latitude')
            (xxx,ymin,ymax) = history.get_max_min(1)
            (NS,latitude)   = format_latitude(latitude)
            fig = figure(fignum)
            ax = fig.add_subplot(1,1,1)
            ax.plot(xxx,ymin,colour+style,label='{0:5.1f}{1}'.format(abs(latitude),NS))


def display_daily_minima_all_latitudes(fignum,pattern='^[0-9]+-[0-9]+-[0-9]+-.*co2-[0-9]+([NS])?.txt'):
      index=0
      for name in glob('*.txt'):
            m = match(pattern,name)
            if m:
                  style='--' if m.group(1)=='S' else ''
                  display_daily_minima(name,fignum,get_colour(index),style)
                  fignum += 1
                  index+=1
      fig = figure(fignum,figsize=(6,6))
      ax = fig.add_subplot(1,1,1)
      ax.set_title('Minimum temperature for each Latitude')
      ax.set_xlabel('Time')
      ax.set_ylabel('Temperature - Kelvin')
      ax.legend(loc='lower left')
      ax.grid(True)
      fig.savefig('SurfaceTemperatureAllLatitudes')

def main(argv):
      inputfile    = 'output.txt'
      fignum       = 1
      all          = False
      minmax       = False
      daily_minima = False
      if len(argv)>0:
            try:
                  opts, args = getopt( \
                        argv,\
                        'hi:amd',\
                        ['help','ifile=','allpoints','maxmin','daily'])

            except GetoptError:
                  help()
                  exit(2)
            for opt, arg in opts:
                  if opt == '-h':
                        help()
                        exit()
                  elif opt in ('-i', '--ifile'):
                        inputfile = arg
                  elif opt == '-a':
                        all = True
                  elif opt == '-m':
                        minmax = True
                  elif opt == '-d':
                        daily_minima = True

      if all:
            display(inputfile,fignum)
            fignum += 1
      if minmax:
            display_maxmin(inputfile,fignum)
            fignum +=1
      if daily_minima:
            display_daily_minima_all_latitudes(fignum)
            fignum +=1

      show()

# Tested: -m    OK
#         -d    OK
#         -a    OK

if __name__=='__main__':
      main(argv[1:])
