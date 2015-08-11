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
thatArray = numpy.zeros((nPixelsYnew, nPixelsXnew))

if(VerboseProcessing):
  print "\t'" + InputFilePath + "' is", nPixelsXold, "x", nPixelsYold, "pixels."
  print "\t'" + OutputFilePath + "' will be", nPixelsXnew, "x", nPixelsYnew, "pixels (""{:0.0f}".format(lCCDX)  + " mm x " + "{:0.0f}".format(lCCDY) + " mm)."

# Set the row and column offset since the controler seems to wrap rows and columns (mostly
# columns) around the images we read out.
RowOffset = 0
ColumnOffset = 39

# A list of overscan pixel values for us to histogram at the end.
OversanPixelValues = []

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
    # First, we deal with the overscan.
    NewRow, NewColumn = PythonTools.RemoveSpectroCCDOverscan(row, column, nPixelsYold, nPixelsXold, nRealPixelsY, nRealPixelsX)
    if((NewRow == -10) or (NewColumn == -10)):
      #PythonTools.RemoveSpectroCCDOverscan returns a -10 as the to either NewRow and/or NewColumn
      # if it finds the pixel location to be in one of the overscan regions, and just subtracts out
      # the overscan pixel number if it is not.
      OversanPixelValues.append(thisPixelValue)
      if(Debugging): print "Row", row, "and Column", column, "is in the overscan region!"
      continue
    else: 
      if(Debugging): print "Row", row, "and Column", column, "maps to", NewRow, "and", NewColumn, "after removing the overscan."
    # First we fix the offset and wrap-around.
    NewRow, NewColumn = PythonTools.FixSpectroCCDOffset(NewRow, NewColumn, nRealPixelsY * 2, nRealPixelsX / 2, RowOffset, ColumnOffset)
    if(Debugging): 
      print "\t...and writing it to row", NewRow, "and column", NewColumn, "after fixing the wrap-around."
    # Next we fix the relative reflection of the bottom half of the image (we may not have to do this forever...).
    NewRow, NewColumn = PythonTools.FlipSpectroCCDBottom(NewRow, NewColumn, nRealPixelsY * 2, nRealPixelsX / 2)
    if(Debugging): 
      print "\t...and writing it to row", NewRow, "and column", NewColumn, "after flipping the bottom of the image."
    # Shuffle the columns together to interdigitate.
    NewRow, NewColumn = PythonTools.InterdigitateSpectroCCDPixels(NewRow,           NewColumn, 
                                                                  nRealPixelsY * 2, nRealPixelsX / 2, 
                                                                  nPixelsYnew,      nPixelsXnew)
    if(Debugging): print "\t...and writing it to row", NewRow, "and column", NewColumn, "after interdigitating."
    # Fix the last remaining pixel offsets between the odd and even pixels.
    PixelShift = 3 #This is the number of pixels that we will shift the odd down (increment the row number).
    NewRow = PythonTools.FixSpectroCCDPixelOffset(PixelShift, NewRow, NewColumn, nPixelsYnew)
    if(Debugging): print "\t...and writing it to row", NewRow, "and column", NewColumn, "now that we're done."
    thatArray[NewRow][NewColumn] = thisPixelValue
if(Debugging): 
  print thisImage[0].data
  print thatArray

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

# Now Loop over the pixel values in the overscan region and put them into a histogram.
if(len(OversanPixelValues) != 0):
  import ROOT
  import RootPlotLibs
  import PythonTools
  ROOT.gROOT.Reset()
  ROOT.gROOT.ProcessLine(".L ./CompiledTools.C+")
  OSPVBinWidth = 20.
  OSPVIncr = 1.
  OSPVMin = numpy.round(min(OversanPixelValues), 0)
  while((OSPVMin % OSPVBinWidth) != (0.5 * OSPVBinWidth)):
    OSPVMin -= OSPVIncr
    #print OSPVMin
  OSPVMax = numpy.round(max(OversanPixelValues), 0)
  while((OSPVMax % OSPVBinWidth) != (0.5 * OSPVBinWidth)):
    OSPVMax += OSPVIncr
    #print OSPVMax
  nOSPVBins = int((OSPVMax - OSPVMin) / OSPVBinWidth)
  OSPVHisto = PythonTools.MakePixValHisto("OSPVHisto", "Overscan Pixel Values", nOSPVBins, OSPVMin, OSPVMax, ROOT.kBlack)
  OSPVHisto.GetXaxis().SetTitle("Raw ADC Value")
  for ospv in OversanPixelValues:
    OSPVHisto.Fill(ospv)
  aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
  aCanvas.Draw()
  aCanvas.cd()
  aPad.SetLeftMargin(0.08)
  aPad.SetRightMargin(0.01)
  aPad.SetBottomMargin(0.08)
  aPad.Draw()
  aPad.cd()
  OSPVHisto.Draw()
  aCanvas.Update()
  aCanvas.SaveAs(OutputFilePath.replace("_UnShuf.fits", "_OverscanPixValHisto.pdf"))
  aRootFile = ROOT.TFile(OutputFilePath.replace("_UnShuf.fits", "_OverscanPixValHisto.root"), "recreate")
  OSPVHisto.Write()
  aRootFile.Close()

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
