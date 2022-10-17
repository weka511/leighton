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

'''
   User interface for Viewer

   Allows user to select text files from previous runs of leighton.py and
   display them graphically.

 '''

from fnmatch           import fnmatch
from matplotlib.pyplot import show
from multiprocessing   import Process, freeze_support
from os                import listdir
from tkinter           import Button, Frame, Listbox, Scrollbar, Tk
from viewer            import display

# The next few methods need to be declared before multiprocessing calls
# as they run as separate processes.

def exec_display_ext(inputfile,figure):
    '''
    Execute the display function and show plot
    '''
    print('Display {0} as figure {1}'.format(inputfile,figure))
    display(inputfile,figure=figure)
    show()

def exec_display_maxmin_ext(inputfile,figure):
    '''
    Execute the display maxmin function and show plot
    '''
    print('Display Max Min{0} as figure {1}'.format(inputfile,figure))
    display_maxmin(inputfile,figure=figure)
    show()

def exec_display_daily_minima_ext(inputfile,figure):
    '''
    Execute the display all function and show plot
    Use the selected file as a template, so we get all runs (all latitudes)
    with other parameters matching.
    '''
    print('Display Daily {0} as figure {1}'.format(inputfile,figure))
    m=re.match('(^[0-9]+-[0-9]+-[0-9]+-.*co2-)([0-9]+[NS]?)(.txt)',inputfile)
    pattern='{0}[0-9]+([NS])?{1}'.format(m.group(1),m.group(3))
    print (m.group(1),m.group(2),m.group(3),pattern)
    display_daily_minima_all_latitudes(figure=figure,pattern=pattern)
    show()


class Viewer(Frame):
    '''
    This class represents a Frame and UI elements
    '''
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        self.figure=1
        self.tasks=[]


    def createWidgets(self):
        scrollbar = Scrollbar(root, orient="vertical")
        self.file_list=Listbox(self, width=50, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_list.yview)

        for file in listdir('.'):
            if fnmatch(file, '*.txt'):
                self.file_list.insert('end',file)

        self.file_list.grid(row=0,column=1)

        self.all_button            = Button(self)
        self.all_button['text']    = 'All'
        self.all_button['command'] = self.exec_all
        self.all_button.grid(row=1,column=0)

        self.minmax_button            = Button(self)
        self.minmax_button['text']    = 'MinMax'
        self.minmax_button['command'] = self.exec_maxmin
        self.minmax_button.grid(row=1,column=1)

        self.daily_button            = Button(self)
        self.daily_button['text']    = 'Daily'
        self.daily_button['command'] = self.exec_daily_minima
        self.daily_button.grid(row=1,column=2)

        self.close = Button(self, text='Close', command=self.close_all)
        self.close.grid(row=2,column=1)


    def close_all(self):
        '''
        When user presses Close, terminate all threads, then exit
        '''
        for task in self.tasks:
            if task.is_alive():
                task.terminate()
                task.join()
        root.destroy()

    def exec_all(self):
        '''
        All button pressed
        '''
        inputfile = self.file_list.get(self.file_list.curselection())
        self.tasks.append(Process(target  = exec_display_ext,
                                     args = (inputfile,self.figure)))
        self.tasks[-1].start()
        self.figure+=1


    def exec_maxmin(self):
        '''
        MaxMin button pressed
        '''
        inputfile=self.file_list.get(self.file_list.curselection())
        self.tasks.append(Process(target=exec_display_maxmin_ext,
                                     args=(inputfile,self.figure)))
        self.tasks[-1].start()
        self.figure+=1

    def exec_daily_minima(self):
        '''
        Daily minima pressed
        '''
        inputfile=self.file_list.get(self.file_list.curselection())
        self.tasks.append(Process(target=exec_display_daily_minima_ext,
                                      args=(inputfile,self.figure)))
        self.tasks[-1].start()
        self.figure+=1


if __name__=='__main__':
    freeze_support() # Need this for MS Windows
    root = Tk()
    root.title('Leighton and Murray Viewer')
    app = Viewer(master=root)
    app.mainloop()

