#!/usr/bin/python

###################################################################################################
# Support functions for fits file analysis.                                                       #
###################################################################################################

def GetSpectroCCDPixel(row, column, nrowsold, ncolumnsold, rowoffset, columnoffset, nrowsnew, ncolumnsnew):
  # Correct for the row and column offsets...
  row -= rowoffset
  if(row < 0): row += nrowsold
  column -= columnoffset
  if(column < 0): column += ncolumnsold
  # Decide which quadrant of the old image we're in.
  Quadrant = 0
  if((row <  (nrowsold / 2)) and (column >= (ncolumnsold / 2))): 
    Quadrant = 1
  if((row <  (nrowsold / 2)) and (column <  (ncolumnsold / 2))): 
    Quadrant = 2
  if((row >= (nrowsold / 2)) and (column <  (ncolumnsold / 2))): 
    Quadrant = 3
  if((row >= (nrowsold / 2)) and (column >= (ncolumnsold / 2))): 
    Quadrant = 4
  if(Quadrant == 0): print "\tWhat happened in row", row, "and column", str(column) + "?  It seems to still be a", Quadrant
  # Based on which quadrant we're in, decide what new pixel the old pixed maps into.
  NewRow = 0
  NewColumn = 0
  if(Quadrant == 1):
    NewRow = row
    NewColumn = (2 * (column - (ncolumnsold / 2))) + 1 + ncolumnsold
  if(Quadrant == 2):
    NewRow = row
    NewColumn = (2 * column) + 1
  if(Quadrant == 3):
    NewRow = row - (nrowsold / 2)
    NewColumn = 2 * column
  if(Quadrant == 4):
    NewRow = row - (nrowsold / 2)
    NewColumn = (2 * (column - (ncolumnsold / 2))) + ncolumnsold
  while(NewRow >= nrowsnew): NewRow -= nrowsnew
  while(NewColumn >= ncolumnsnew): NewColumn -= ncolumnsnew
  #if(NewColumn > ncolumnsnew / 2):
  #  print "Mapping row", row, "out of", nrowsold, "and column", column, "out of", ncolumnsold, "(quadrant " + str(Quadrant) + ") into row", NewRow, "and column", NewColumn
  return NewRow, NewColumn

def Progress(thispixel, totalpixels):
  step = totalpixels / 10
  if((thispixel % step) == 0): 
    print "\t\tProcessed", thispixel, "out of", totalpixels, "pixels (" + str(int(100. * float(thispixel) / float(totalpixels))) + "%)."
  return
