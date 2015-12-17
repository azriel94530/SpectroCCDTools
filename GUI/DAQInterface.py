#!/usr/bin/python

###################################################################################################
# This is a first pass at a potential GUI data aquisition system for the SpectroCCD.              #
###################################################################################################

import Tkinter
import ttk
import time
import os
import numpy as np

class simpleapp_tk(Tkinter.Tk):
  def __init__(self,parent):
    Tkinter.Tk.__init__(self,parent)
    self.parent = parent
    self.initialize()

  def initialize(self):
    # Pick the 'grid' layout organizer
    self.grid()
    # Add a field to enter the exposure time...
    self.ExpTimeEntryVar = Tkinter.StringVar()
    self.entry = Tkinter.Entry(self, textvariable=self.ExpTimeEntryVar)
    self.entry.grid(column=0,row=0,sticky='EW')
    self.entry.bind("<Return>", self.SetExpTime)
    self.ExpTimeEntryVar.set(u"Enter Exposure Time [s]")
    # Add a field that display the exposure time.
    self.ExposureTime = Tkinter.StringVar()
    self.ExposureTime.set("Exp. Time Not Set")
    ExpTimeLabel = Tkinter.Label(self, textvariable=self.ExposureTime, 
                                 anchor="w", fg="black", bg="white")
    ExpTimeLabel.grid(column=2, row=0, columnspan=1, sticky='EW')
    # Add a separator between the entry and display fields.
    TopSeparator = ttk.Separator(orient="vertical")
    TopSeparator.grid(column=1, row=0)
    # Add a button to start the CCD exposure.
    CCDReadButton = Tkinter.Button(self,text=u"Read CCD", command=self.CCDRead)
    CCDReadButton.grid(column=0,row=1)
    # Add a label as an output area.
    self.labelVariable = Tkinter.StringVar()
    self.labelVariable.set("Output will show up here...")
    self.OutputLabel = Tkinter.Label(self, textvariable=self.labelVariable, 
                          anchor="w", fg="white", bg="blue")
    self.OutputLabel.grid(column=2, row=1, columnspan=2, sticky='EW')
    self.labelVariable.set(u" ")
    # Add a separator between the read button and message fields.
    BottomSeparator = ttk.Separator(orient="vertical")
    BottomSeparator.grid(column=1, row=2)
    # Add a label for image display.
    self.InitialPhoto = Tkinter.PhotoImage(file="Initial.gif")
    self.PhotoLabel = Tkinter.Label(self, image=self.InitialPhoto)
    self.PhotoLabel.grid(column=3, row=0)
    # Add a progress bar...
    self.progressbar = ttk.Progressbar(self, orient='horizontal',
                                  length=300, mode='determinate')
    self.progressbar.pack(expand=True, fill=Tkinter.BOTH, side=Tkinter.TOP)
    self.progressbar.grid(column=0, row=2, columnspan=4, sticky='EW')
    # Allow the window to be resized.
    self.grid_columnconfigure(0,weight=1)
    self.resizable(True,True)
    self.update()
    self.geometry(self.geometry())
    # Fix some mouse focus issues.
    self.entry.focus_set()
    self.entry.selection_range(0, Tkinter.END)

  def CCDRead(self):
    self.labelVariable.set("Reading in the (fake) image...")
    self.update()
    ExpTime = float(self.ExpTimeEntryVar.get())
    self.progressbar["value"] = 0.
    self.progressbar["maximum"] = ExpTime
    for i in range(int(ExpTime)):
      time.sleep(1)
      self.progressbar["value"] = float(i + 1)
      self.update()
    self.labelVariable.set(" ")
    self.update()
    self.DisplayImage()
    self.entry.focus_set()
    self.entry.selection_range(0, Tkinter.END)

  def DisplayImage(self):
    imagePath = os.getcwd() + "/testpattern.gif"
    #print imagePath
    self.PhotoLabel.image = self.InitialPhoto
    self.OutputPhoto = Tkinter.PhotoImage(file=imagePath)
    self.PhotoLabel.configure(image=self.OutputPhoto)
    self.PhotoLabel.grid(column=3, row=0)
    self.update()

  def SetExpTime(self,event):
    self.ExposureTime.set("Exp. Time: " + self.ExpTimeEntryVar.get() + " seconds")
    self.entry.focus_set()
    self.entry.selection_range(0, Tkinter.END)

if __name__ == "__main__":
  app = simpleapp_tk(None)
  app.title('SpectroCCD DAQ')
  app.mainloop()

#exit()