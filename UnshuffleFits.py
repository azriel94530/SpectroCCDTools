#!/usr/bin/python

####################################################################################################
# Open a FITS file and unshuffle the pixels according to the readout as described in numerous      #
# conversations with John Joseph and Peter Denes.  Then write the resultant unshuffled FITS to a   #
# new file.                                                                                        #
####################################################################################################

# Header, import statements etc.
import time
import sys
import os
import astropy.io.fits
import numpy
import PythonTools

####################################
#  BEGIN MAIN BODY OF THE CODE!!!  #
####################################

# Get the start time of this calculation
StartTime = time.time()

# Set some flags for how verbose our input and output are going to be.
Debugging = False
VerboseProcessing = True

if(len(sys.argv) != 2):
  print "Usage: python UnshuffleFits.py path/to/fits/image"
  exit()

# Pull in the path to the FITS file we're going to look at
InputFilePath = sys.argv[1]
OutputFilePath = InputFilePath.replace(".fits", "_UnShuf.fits")
if os.path.exists(OutputFilePath):
  os.system("rm " + OutputFilePath)
if(VerboseProcessing):
  print "\tReading in: '" + InputFilePath + "'."
  print "\tWriting output to: '" + OutputFilePath + "'."

# Use astropy to open up the fits file we're after.
thisImage = astropy.io.fits.open(InputFilePath)
if(Debugging): print thisImage.info()

# Set the number of pixels for the output image, and make a numpy array of those dimensions.
nPixelsXnew = 2496
nPixelsYnew = 620
nPixelsnew = nPixelsXnew * nPixelsYnew
thatArray = numpy.zeros((nPixelsYnew, nPixelsXnew))

# We know that the pixel dimensions are 5 um by 45 um.  It would be nice if we could read this out
# of the fits header!
lPixelX =  5. / 1000. #[mm]
lPixelY = 45. / 1000. #[mm]

# Now calculate the CCD dimensions.
lCCDX = nPixelsXnew * lPixelX
lCCDY = nPixelsYnew * lPixelY

# Extract the dimensions of this fits image from the header information
nPixelsXold = thisImage[0].header['NAXIS1']
nPixelsYold = thisImage[0].header['NAXIS2']
nPixelsold = nPixelsXold * nPixelsYold
if(VerboseProcessing):
  print "\t'" + InputFilePath + "' is", nPixelsXold, "x", nPixelsYold, "pixels."
  print "\t'" + OutputFilePath + "' will be", nPixelsXnew, "x", nPixelsYnew, "pixels (""{:0.0f}".format(lCCDX)  + " mm x " + "{:0.0f}".format(lCCDY) + " mm)."

# Set the row and column offset since the controler seems to wrap rows and columns (mostly
# columns) around the images we read out.
RowOffset = 0
ColumnOffset = 39

# Step over all the pixels in the old fits image and put and assign their values to the
# appropriate location in the new one.
iPixel = 0
for column in range(nPixelsXold):
  for row in range(nPixelsYold):
    iPixel += 1
    PythonTools.Progress(iPixel, nPixelsold)
    thisPixelValue = thisImage[0].data[row][column]
    if(Debugging): 
      print "Reading in value:", thisPixelValue, "from row", row, "and column", column
    # First we fix the offset and wrap-around.
    NewRow, NewColumn = PythonTools.FixSpectroCCDOffset(row, column, nPixelsYold, nPixelsXold, RowOffset, ColumnOffset)
    if(Debugging): 
      print "\t...and writing it to row", NewRow, "and column", NewColumn, "after fixing the wrap-around."
    # Next we fix the relative reflection of the bottom half of the image (we may not have to do this forever...).
    NewRow, NewColumn = PythonTools.FlipSpectroCCDBottom(NewRow, NewColumn, nPixelsYold, nPixelsXold)
    if(Debugging): 
      print "\t...and writing it to row", NewRow, "and column", NewColumn, "after flipping the bottom of the image."
    # Shuffle the columns together to interdigitate.
    NewRow, NewColumn = PythonTools.InterdigitateSpectroCCDPixels(NewRow,      NewColumn, 
                                                                  nPixelsYold, nPixelsXold, 
                                                                  nPixelsYnew, nPixelsXnew)
    # Fix the last remaining pixel offsets between the odd and even pixels.
    PixelShift = 1 #This is the number of pixels that we will shift the odd columns up and the even columns down.
    NewRow = PythonTools.FixSpectroCCDPixelOffset(PixelShift, NewRow, NewColumn, nPixelsYnew)
    if(Debugging): print "\t...and writing it to row", NewRow, "and column", NewColumn, "now that we're done."
    thatArray[NewRow][NewColumn] = thisPixelValue
if(Debugging): 
  print thisImage[0].data
  print thatArray

# Write the new FITS file.
thatHDU = astropy.io.fits.PrimaryHDU(thatArray)
thatImage = astropy.io.fits.HDUList([thatHDU])
thatImage[0].header.append(('PXLDIM1', lPixelX))
thatImage[0].header.append(('PXLDIM2', lPixelY))
thatImage.writeto(OutputFilePath)
if(Debugging):
  for entry in thatImage[0].header:
    print entry + "\t" + str(thatImage[0].header[entry])

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
