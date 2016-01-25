#!/usr/bin/python

####################################################################################################
# Open a FITS file and unshuffle the pixels according to the readout as described in numerous      #
# conversations with John Joseph and Peter Denes.  Then write the resultant unshuffled FITS to a   #
# new file.  We also take care of any overscan here.  The overscan pixels are simply removed, and  #
# their values written to a histogram that is subsequently plotted and drawn to a pdf and written  #
# to a root file.                                                                                  #
####################################################################################################

# Header, import statements etc.
import time
import sys
import os
import astropy.io.fits
import numpy as np
import matplotlib.pyplot as plt
import PythonTools

####################################
#  BEGIN MAIN BODY OF THE CODE!!!  #
####################################

# Get the start time of this calculation
StartTime = time.time()

# Set some flags for how verbose our input and output are going to be.
Debugging = False
VerboseProcessing = True

if(len(sys.argv) != 3):
  print "Usage: python UnshuffleFits.py path/to/fits/image N"
  print "       where \'N\' is the number of pixels to shift the odd columns down."
  exit()

# Pull in the path to the FITS file we're going to look at
InputFilePath = sys.argv[1]
OutputDir = InputFilePath.replace(".fits", "")
if(not(os.path.isdir(OutputDir))):
  os.system("mkdir " + OutputDir)
OutputFilePath = OutputDir + "/" + InputFilePath.split("/")[-1].replace(".fits", "_UnShuf.fits")
if os.path.exists(OutputFilePath):
  print "Deleting old version of", OutputFilePath
  os.system("rm " + OutputFilePath)
if(VerboseProcessing):
  print "\tReading in: '" + InputFilePath + "'."
  print "\tWriting output to: '" + OutputFilePath + "'."

#This is the number of pixels that we will shift the odd down (increment the row number).
PixelShift = int(sys.argv[2]) 
if(VerboseProcessing):
  print "\tShifting *odd* pixels in the reconstructed image down (incrementing row number) by", PixelShift, "Pixel(s)."

# Use astropy to open up the fits file we're after.
thisImage = astropy.io.fits.open(InputFilePath, ignore_missing_end=True)
if(Debugging): print thisImage.info()

# Extract the dimensions of this fits image from the header information
nPixelsXold = thisImage[0].header['NAXIS1']
nPixelsYold = thisImage[0].header['NAXIS2']
nPixelsold = nPixelsXold * nPixelsYold

# We know that the pixel dimensions are 5 um by 45 um.  It would be nice if we could read this out
# of the fits header!
lPixelX =  5. / 1000. #[mm]
lPixelY = 45. / 1000. #[mm]

# We also know that the CCD chip is REALLY 2496 x 620 pixels.  This will be very useful when we subtract
# the overscan region.
nRealPixelsX = 2496
nRealPixelsY =  620
lCCDX = nRealPixelsX * lPixelX
lCCDY = nRealPixelsY * lPixelY

# Set the number of pixels for the output image, and make a numpy array of those dimensions.
nPixelsXnew = nRealPixelsX
nPixelsYnew = nRealPixelsY
nPixelsnew = nPixelsXnew * nPixelsYnew
thatArray = np.zeros((nPixelsYnew, nPixelsXnew))

if(VerboseProcessing):
  print "\t'" + InputFilePath + "' is", nPixelsXold, "x", nPixelsYold, "pixels."
  print "\t'" + OutputFilePath + "' will be", nPixelsXnew, "x", nPixelsYnew, "pixels (""{:0.0f}".format(lCCDX)  + " mm x " + "{:0.0f}".format(lCCDY) + " mm)."

# Set the row and column offset since the controler seems to wrap rows and columns (mostly
# columns) around the images we read out.
RowOffset = 0
ColumnOffset = -396

# Convert the image array into the a numpy array...
imageArray = np.array(thisImage[0].data)

# Fix the wrap-around:
imageArray = np.roll(imageArray, RowOffset,    axis=0)
imageArray = np.roll(imageArray, ColumnOffset, axis=1)

# Flip the bottom of the image with respect to the top.
splitImage = np.split(imageArray, 2, 0)
imageTop, imageBot = splitImage[0], splitImage[1]
imageBot = np.fliplr(imageBot)

# Separate out the horizontal overscan and image regions since they end up at different parts of
# the image after interdigitation.  The horizontal overscan is at the bottom of the top image and
# the top of the bottom image.
splitImage = np.split(imageTop, [nRealPixelsY], axis=0)
imageTop_Real, imageTop_OS = splitImage[0], splitImage[1]
splitImage = np.split(imageBot, [(nPixelsYold / 2) - nRealPixelsY], axis=0)
imageBot_Real, imageBot_OS = splitImage[1], splitImage[0]

if(Debugging):
  print "Real Top:", imageTop_Real.shape
  print "Ovsc Top:", imageTop_OS.shape
  print "Real Bot:", imageBot_Real.shape
  print "Ovsc Bot:", imageBot_OS.shape

# Interdigitate the top and bottom together...
TopColumns = np.split(imageTop_Real, imageTop_Real.shape[1], axis=1)
BotColumns = np.split(imageBot_Real, imageBot_Real.shape[1], axis=1)
for icol in range(imageTop_Real.shape[1]):
  # Roll the top column by the pixel shift
  thisTopColumn = np.roll(TopColumns[icol], -1 * PixelShift, axis=0)
  if(icol == 0):
    imageArray = np.hstack((thisTopColumn, BotColumns[icol]))
  else:
    imageArray = np.hstack((imageArray, thisTopColumn))
    imageArray = np.hstack((imageArray, BotColumns[icol]))
if(Debugging):
  print "New Image with vertical overscan is of shape", imageArray.shape

# Pull out the vertical overscan from the center of the top and bottom images.
splitImage = np.split(imageArray, [nRealPixelsX / 2, imageArray.shape[1] - (nRealPixelsX / 2)], axis=1)
imageArray_left  = splitImage[0]
imageArray_overs = splitImage[1]
imageArray_right = splitImage[2]
if(Debugging):
  print " Left half of the real image has the shape:", imageArray_left.shape
  print "Right half of the real image has the shape:", imageArray_right.shape
  print "Vertical overscan has the shape:",  imageArray_overs.shape
# Glue the two halves of the real image together...
thatArray = np.hstack((imageArray_left, imageArray_right))
if(Debugging):
  print "Real image is of the shape:", thatArray.shape

# Write the new FITS file.
thatHDU = astropy.io.fits.PrimaryHDU(thatArray)
thatImage = astropy.io.fits.HDUList([thatHDU])
# Add this pixel dimensions to the header...
thatImage[0].header.append(('PXLDIM1', lPixelX))
thatImage[0].header.append(('PXLDIM2', lPixelY))
thatImage.writeto(OutputFilePath)
if(Debugging):
  for entry in thatImage[0].header:
    print entry + "\t" + str(thatImage[0].header[entry])

# A list of overscan pixel values for us to histogram at the end.
OverscanTop = list(np.ravel(imageTop_OS))
OverscanBot = list(np.ravel(imageBot_OS))
OverscanVer = list(np.ravel(imageArray_overs))
OversanPixelValues = OverscanTop + OverscanBot + OverscanVer

# Histogram the overscan pixel values...
xLo, xHi, xStep = float(min(OversanPixelValues)), float(max(OversanPixelValues)), 10.
xBins = np.arange(xLo, xHi + xStep, xStep)
plt.figure(num=None, figsize=(16, 9), dpi=80, facecolor='w', edgecolor='k')
HistVals = plt.hist(OversanPixelValues, bins=xBins, facecolor='k', alpha=0.75)[0]
plt.axis([xLo, xHi, 0., 1.05 * max(HistVals)])
plt.xlabel('Overscan Pixel Value')
plt.ylabel('Counts per ' + '{:0.1f}'.format(xStep) + ' ADC Unit Bin')
plt.title('Histogram of Overscan Pixel Values')
plt.grid(True)
plt.savefig(OutputFilePath.replace("_UnShuf.fits", "_Overscan.png"))

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
