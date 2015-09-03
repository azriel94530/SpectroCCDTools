#!/usr/bin/python

####################################################################################################
# Open a FITS file from the SpectroCCD, and perform a few analyses of the readouts for each of the #
# four corners of the device.  We will first have to fix the weird wrap-around we get out of the   #
# controler.  After that, we will loop over the pixel values in each of the four amplidfiers       #
# (avoiding the edges because they're kind of wonky) and calculate the RMS and pixel column slope. #
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
if(VerboseProcessing):
  print "\tReading in: '" + InputFilePath + "'."

# Use astropy to open up the fits file we're after.
thisImage = astropy.io.fits.open(InputFilePath, ignore_missing_end=True)
if(Debugging): print thisImage.info()

# Extract the dimensions of this fits image from the header information
nPixelsXold = thisImage[0].header['NAXIS1']
nPixelsYold = thisImage[0].header['NAXIS2']
nPixelsold = nPixelsXold * nPixelsYold
# We also know that the CCD chip is REALLY 2496 x 620 pixels, which because of the readout tricks
# we have to play, makes the image, 1248 x 1240.  This is going to be important when we sort out
# when we are in the overscan region, and which one we are in.
nRealPixelsX = 2496
nRealPixelsY =  620
nNonOSPixelsX = nRealPixelsX / 2
nNonOSPixelsY = nRealPixelsY * 2
nPixelsPerQuadrant = (nNonOSPixelsX * nNonOSPixelsY) / 4
if(VerboseProcessing):
  print "\tImage:", "\'" + InputFilePath + "\'", "is", nPixelsXold, "by", str(nPixelsYold) + "."
  print "\tAfter removing the overscan region, we are left with", nNonOSPixelsX, "by", str(nNonOSPixelsY) + "."

# Now, define the rows and columns over which  the image quadrants and overscans stretch. We're 
# going to just use the cartesean coordinate cconvention, like this: 2 | 1
#                                                                    -----
#                                                                    3 | 4
PrintRegions = False
# Quadrant 1:
Quadrant1ColStart = nPixelsXold - (nNonOSPixelsX / 2)
Quadrant1ColStop  = nPixelsXold
Quadrant1RowStart = 0
Quadrant1RowStop  = nNonOSPixelsY / 2
Q1OSColStart = nPixelsXold / 2
Q1OSColStop  = nPixelsXold - (nNonOSPixelsX / 2)
Q1OSRowStart = 0
Q1OSRowStop  = nNonOSPixelsY / 2
if(PrintRegions):
  print "Quadrant 1:", Quadrant1ColStart, "< x <", Quadrant1ColStop
  print "           ", Quadrant1RowStart, "< y <", Quadrant1RowStop
  print "Overscan 1:", Q1OSColStart, "< x <", Q1OSColStop
  print "           ", Q1OSRowStart, "< y <", Q1OSRowStop
# Quadrant 2:
Quadrant2ColStart = 0
Quadrant2ColStop  = nNonOSPixelsX / 2
Quadrant2RowStart = 0
Quadrant2RowStop  = nNonOSPixelsY / 2
Q2OSColStart = nNonOSPixelsX / 2
Q2OSColStop  = nPixelsXold / 2
Q2OSRowStart = 0
Q2OSRowStop  = nNonOSPixelsY / 2
if(PrintRegions):
  print "Quadrant 2:", Quadrant2ColStart, "< x <", Quadrant2ColStop
  print "           ", Quadrant2RowStart, "< y <", Quadrant2RowStop
  print "Overscan 2:", Q2OSColStart, "< x <", Q2OSColStop
  print "           ", Q2OSRowStart, "< y <", Q2OSRowStop
# Quadrant 3:
Quadrant3ColStart = 0
Quadrant3ColStop  = nNonOSPixelsX / 2
Quadrant3RowStart = nPixelsYold - (nNonOSPixelsY / 2)
Quadrant3RowStop  = nPixelsYold
Q3OSColStart = nNonOSPixelsX / 2
Q3OSColStop  = nPixelsXold / 2
Q3OSRowStart = nPixelsYold - (nNonOSPixelsY / 2)
Q3OSRowStop  = nPixelsYold
if(PrintRegions):
  print "Quadrant 3:", Quadrant3ColStart, "< x <", Quadrant3ColStop
  print "           ", Quadrant3RowStart, "< y <", Quadrant3RowStop
  print "Overscan 3:", Q3OSColStart, "< x <", Q3OSColStop
  print "           ", Q3OSRowStart, "< y <", Q3OSRowStop
# Quadrant 4:
Quadrant4ColStart = nPixelsXold - (nNonOSPixelsX / 2)
Quadrant4ColStop  = nPixelsXold
Quadrant4RowStart = nPixelsYold - (nNonOSPixelsY / 2)
Quadrant4RowStop  = nPixelsYold
Q4OSColStart = nPixelsXold / 2
Q4OSColStop  = nPixelsXold - (nNonOSPixelsX / 2)
Q4OSRowStart = nPixelsYold - (nNonOSPixelsY / 2)
Q4OSRowStop  = nPixelsYold
if(PrintRegions):
  print "Quadrant 4:", Quadrant4ColStart, "< x <", Quadrant4ColStop
  print "           ", Quadrant4RowStart, "< y <", Quadrant4RowStop
  print "Overscan 4:", Q4OSColStart, "< x <", Q4OSColStop
  print "           ", Q4OSRowStart, "< y <", Q4OSRowStop

# Set the row and column offset since the controler seems to wrap rows and columns (mostly
# columns) around the images we read out.
RowOffset = 0
ColumnOffset = 39
if(VerboseProcessing):
  print "\tFixing wrap-around of", RowOffset, "rows and", ColumnOffset, "columns."
# Set the buffer around the edges of the real image that we will cut out of this analsys.
EdgeBuffer = 1
Quadrant1FiducialRowStart = Quadrant1RowStart + EdgeBuffer
Quadrant1FiducialRowStop  = Quadrant1RowStop  - EdgeBuffer
Quadrant1FiducialColStart = Quadrant1ColStart + EdgeBuffer
Quadrant1FiducialColStop  = Quadrant1ColStop  - EdgeBuffer
Quadrant2FiducialRowStart = Quadrant2RowStart + EdgeBuffer
Quadrant2FiducialRowStop  = Quadrant2RowStop  - EdgeBuffer
Quadrant2FiducialColStart = Quadrant2ColStart + EdgeBuffer
Quadrant2FiducialColStop  = Quadrant2ColStop  - EdgeBuffer
Quadrant3FiducialRowStart = Quadrant3RowStart + EdgeBuffer
Quadrant3FiducialRowStop  = Quadrant3RowStop  - EdgeBuffer
Quadrant3FiducialColStart = Quadrant3ColStart + EdgeBuffer
Quadrant3FiducialColStop  = Quadrant3ColStop  - EdgeBuffer
Quadrant4FiducialRowStart = Quadrant4RowStart + EdgeBuffer
Quadrant4FiducialRowStop  = Quadrant4RowStop  - EdgeBuffer
Quadrant4FiducialColStart = Quadrant4ColStart + EdgeBuffer
Quadrant4FiducialColStop  = Quadrant4ColStop  - EdgeBuffer
if(VerboseProcessing):
  print "\tIgnoring the", EdgeBuffer, "pixels around the edge of the CCD."
if(PrintRegions):
  print "\tQuadrant 1 analysis goes from row", Quadrant1FiducialRowStart, "to", Quadrant1FiducialRowStop, "and column", Quadrant1FiducialColStart, "to", Quadrant1FiducialColStop
  print "\tQuadrant 2 analysis goes from row", Quadrant2FiducialRowStart, "to", Quadrant2FiducialRowStop, "and column", Quadrant2FiducialColStart, "to", Quadrant2FiducialColStop
  print "\tQuadrant 3 analysis goes from row", Quadrant3FiducialRowStart, "to", Quadrant3FiducialRowStop, "and column", Quadrant3FiducialColStart, "to", Quadrant3FiducialColStop
  print "\tQuadrant 4 analysis goes from row", Quadrant4FiducialRowStart, "to", Quadrant4FiducialRowStop, "and column", Quadrant4FiducialColStart, "to", Quadrant4FiducialColStop

# Some python lists to store the things that we want to keep for analysis.
CCDPixelValues1 = [] #Pixel values for the four quadrants
CCDPixelValues2 = []
CCDPixelValues3 = []
CCDPixelValues4 = []
VOSPixelValues1 = [] #Vertical overscan pixel values for the four quadrants
VOSPixelValues2 = []
VOSPixelValues3 = []
VOSPixelValues4 = []
StartValues1 = [] #Starting values for the slope calculation in each quadrant
StartValues2 = []
StartValues3 = []
StartValues4 = []
FinalValues1 = [] #Final values for the slope calculation in each quadrant
FinalValues2 = []
FinalValues3 = []
FinalValues4 = []

# Counters for a few things to make sure that we're doing stuff right.
nQuadrant1Pixels = 0 #Counters for the four quadrants
nQuadrant2Pixels = 0
nQuadrant3Pixels = 0
nQuadrant4Pixels = 0
nQuadrant1OSPixels = 0# Counter for the four overscans
nQuadrant2OSPixels = 0
nQuadrant3OSPixels = 0
nQuadrant4OSPixels = 0

# Step over all the pixels in the fits image and put and assign their values to the
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
    NewRow, NewColumn = PythonTools.FixSpectroCCDOffset(row, column, nRealPixelsY * 2, nRealPixelsX / 2, RowOffset, ColumnOffset)
    if(Debugging): 
      print "\t...and writing it to row", NewRow, "and column", NewColumn, "after fixing the wrap-around."
    # Now we figure out which image quadrant or overscan region, this pixel is in
    # Quadrant 1 analysis:
    if((NewColumn >= Quadrant1ColStart) and (NewColumn < Quadrant1ColStop) and (NewRow >= Quadrant1RowStart) and (NewRow < Quadrant1RowStop)):
      nQuadrant1Pixels += 1
    if((NewColumn >= Quadrant1FiducialColStart) and (NewColumn < Quadrant1FiducialColStop) and (NewRow >= Quadrant1FiducialRowStart) and (NewRow < Quadrant1FiducialRowStop)):
      CCDPixelValues1.append(thisPixelValue)
      if(NewRow ==  Quadrant1FiducialRowStart):     StartValues1.append(thisPixelValue)
      if(NewRow == (Quadrant1FiducialRowStop - 1)): FinalValues1.append(thisPixelValue)
    # Quadrant 2 analysis:
    if((NewColumn >= Quadrant2ColStart) and (NewColumn < Quadrant2ColStop) and (NewRow >= Quadrant2RowStart) and (NewRow < Quadrant2RowStop)):
      nQuadrant2Pixels += 1
    if((NewColumn >= Quadrant2FiducialColStart) and (NewColumn < Quadrant2FiducialColStop) and (NewRow >= Quadrant2FiducialRowStart) and (NewRow < Quadrant2FiducialRowStop)):
      CCDPixelValues2.append(thisPixelValue)
      if(NewRow ==  Quadrant2FiducialRowStart):     StartValues2.append(thisPixelValue)
      if(NewRow == (Quadrant2FiducialRowStop - 1)): FinalValues2.append(thisPixelValue)
    # Quadrant 3 analysis:
    if((NewColumn >= Quadrant3ColStart) and (NewColumn < Quadrant3ColStop) and (NewRow >= Quadrant3RowStart) and (NewRow < Quadrant3RowStop)):
      nQuadrant3Pixels += 1
    if((NewColumn >= Quadrant3FiducialColStart) and (NewColumn < Quadrant3FiducialColStop) and (NewRow >= Quadrant3FiducialRowStart) and (NewRow < Quadrant3FiducialRowStop)):
      CCDPixelValues3.append(thisPixelValue)
      if(NewRow ==  Quadrant3FiducialRowStart):     StartValues3.append(thisPixelValue)
      if(NewRow == (Quadrant3FiducialRowStop - 1)): FinalValues3.append(thisPixelValue)
    # Quadrant 4 analysis:
    if((NewColumn >= Quadrant4ColStart) and (NewColumn < Quadrant4ColStop) and (NewRow >= Quadrant4RowStart) and (NewRow < Quadrant4RowStop)):
      nQuadrant4Pixels += 1
    if((NewColumn >= Quadrant4FiducialColStart) and (NewColumn < Quadrant4FiducialColStop) and (NewRow >= Quadrant4FiducialRowStart) and (NewRow < Quadrant4FiducialRowStop)):
      CCDPixelValues4.append(thisPixelValue)
      if(NewRow ==  Quadrant4FiducialRowStart):     StartValues4.append(thisPixelValue)
      if(NewRow == (Quadrant4FiducialRowStop - 1)): FinalValues4.append(thisPixelValue)
    # Overscan 1 analysis:
    if((NewColumn >= Q1OSColStart) and (NewColumn < Q1OSColStop) and (NewRow >= Q1OSRowStart) and (NewRow < Q1OSRowStop)):
      nQuadrant1OSPixels += 1
    if((NewColumn >= (Q1OSColStart + EdgeBuffer)) and (NewColumn < (Q1OSColStop - EdgeBuffer)) and (NewRow >= (Q1OSRowStart + EdgeBuffer)) and (NewRow < (Q1OSRowStop - EdgeBuffer))):
      VOSPixelValues1.append(thisPixelValue)
    # Overscan 2 analysis:
    if((NewColumn >= Q2OSColStart) and (NewColumn < Q2OSColStop) and (NewRow >= Q2OSRowStart) and (NewRow < Q2OSRowStop)):
      nQuadrant2OSPixels += 1
    if((NewColumn >= (Q2OSColStart + EdgeBuffer)) and (NewColumn < (Q2OSColStop - EdgeBuffer)) and (NewRow >= (Q2OSRowStart + EdgeBuffer)) and (NewRow < (Q2OSRowStop - EdgeBuffer))):
      VOSPixelValues2.append(thisPixelValue)
    # Overscan 3 analysis:
    if((NewColumn >= Q3OSColStart) and (NewColumn < Q3OSColStop) and (NewRow >= Q3OSRowStart) and (NewRow < Q3OSRowStop)):
      nQuadrant3OSPixels += 1
    if((NewColumn >= (Q3OSColStart + EdgeBuffer)) and (NewColumn < (Q3OSColStop - EdgeBuffer)) and (NewRow >= (Q3OSRowStart + EdgeBuffer)) and (NewRow < (Q3OSRowStop - EdgeBuffer))):
      VOSPixelValues3.append(thisPixelValue)
    # Overscan 4 analysis:
    if((NewColumn >= Q4OSColStart) and (NewColumn < Q4OSColStop) and (NewRow >= Q4OSRowStart) and (NewRow < Q4OSRowStop)):
      nQuadrant4OSPixels += 1
    if((NewColumn >= (Q4OSColStart + EdgeBuffer)) and (NewColumn < (Q4OSColStop - EdgeBuffer)) and (NewRow >= (Q4OSRowStart + EdgeBuffer)) and (NewRow < (Q4OSRowStop - EdgeBuffer))):
      VOSPixelValues4.append(thisPixelValue)

# Quickly report some results to make sure we're making sense...
if(VerboseProcessing):
  print "\tThe real CCD has", nNonOSPixelsX * nNonOSPixelsY, "pixels, so each quadrant should have", str(nPixelsPerQuadrant) + "."
  print "\tWe just counted:"
  print "\t\t", nQuadrant1Pixels, "in quadrant 1"
  print "\t\t", nQuadrant2Pixels, "in quadrant 2"
  print "\t\t", nQuadrant3Pixels, "in quadrant 3"
  print "\t\t", nQuadrant4Pixels, "in quadrant 4"
  if((nQuadrant1Pixels == nPixelsPerQuadrant) and 
     (nQuadrant2Pixels == nPixelsPerQuadrant) and 
     (nQuadrant3Pixels == nPixelsPerQuadrant) and
     (nQuadrant4Pixels == nPixelsPerQuadrant)):
    print "\tGreat!  That checks out...  We also counted:"
  else:
    print "\tHrrrrmmmmm...  We seem to have the wrong number of pixels in one of the quadrants.  Let's stop and reconsider this."
    exit()
  print "\t\t", nQuadrant1OSPixels, "in overscan 1"
  print "\t\t", nQuadrant2OSPixels, "in overscan 2"
  print "\t\t", nQuadrant3OSPixels, "in overscan 3"
  print "\t\t", nQuadrant4OSPixels, "in overscan 4"
  if((nQuadrant1OSPixels == nQuadrant2OSPixels) and
     (nQuadrant1OSPixels == nQuadrant3OSPixels) and
     (nQuadrant1OSPixels == nQuadrant4OSPixels)):
    print "\tWe also seem to have the same number of overscan pixels in each quadrant.  Also great!"
  else:
    print "\tWe unfortunately seem to be miscounting overscan pixels.  Let's figure this out."
    exit()

# Do the mean and RMS for all four qudrants and the overscans...
Qu1PVMean = numpy.mean(CCDPixelValues1)
Qu1PVrms = numpy.sqrt(numpy.mean(numpy.square(CCDPixelValues1)))
Qu2PVMean = numpy.mean(CCDPixelValues2)
Qu2PVrms = numpy.sqrt(numpy.mean(numpy.square(CCDPixelValues2)))
Qu3PVMean = numpy.mean(CCDPixelValues4)
Qu3PVrms = numpy.sqrt(numpy.mean(numpy.square(CCDPixelValues3)))
Qu4PVMean = numpy.mean(CCDPixelValues4)
Qu4PVrms = numpy.sqrt(numpy.mean(numpy.square(CCDPixelValues4)))
OS1PVMean = numpy.mean(VOSPixelValues1)
OS1PVrms = numpy.sqrt(numpy.mean(numpy.square(VOSPixelValues1)))
OS2PVMean = numpy.mean(VOSPixelValues2)
OS2PVrms = numpy.sqrt(numpy.mean(numpy.square(VOSPixelValues2)))
OS3PVMean = numpy.mean(VOSPixelValues3)
OS3PVrms = numpy.sqrt(numpy.mean(numpy.square(VOSPixelValues3)))
OS4PVMean = numpy.mean(VOSPixelValues4)
OS4PVrms = numpy.sqrt(numpy.mean(numpy.square(VOSPixelValues4)))
RegionalMeans = [Qu1PVMean, Qu2PVMean, Qu3PVMean, Qu4PVMean, OS1PVMean, OS2PVMean, OS3PVMean, OS4PVMean]
RegionalRMSs  = [Qu1PVrms,  Qu2PVrms,  Qu3PVrms,  Qu4PVrms,  OS1PVrms,  OS2PVrms,  OS3PVrms,  OS4PVrms]
RegionalNames = ["Quad 1",  "Quad 2",  "Quad 3",  "Quad 4",  "OvSc 1",  "OvSc 2",  "OvSc 3",  "OvSc 4"]
if(VerboseProcessing):
  print "\tRegion\tMean\t\tRMS"
  for i in range(len(RegionalNames)):
    print "\t", RegionalNames[i], "\t", RegionalMeans[i], "\t", RegionalRMSs[i]
print
# Calculate the slopes for each qudrant.
# Quadrant 1:
Qu1StartVal    = numpy.mean(StartValues1)
Qu1FinalVal    = numpy.mean(FinalValues1)
Qu1FiducilRows = Quadrant1FiducialRowStop - Quadrant1FiducialRowStart
Qu1Slope = (Qu1FinalVal - Qu1StartVal) / Qu1FiducilRows
# Quadrant 2:
Qu2StartVal    = numpy.mean(StartValues2)
Qu2FinalVal    = numpy.mean(FinalValues2)
Qu2FiducilRows = Quadrant2FiducialRowStop - Quadrant2FiducialRowStart
Qu2Slope = (Qu2FinalVal - Qu2StartVal) / Qu2FiducilRows
# Quadrant 3:
Qu3StartVal    = numpy.mean(StartValues3)
Qu3FinalVal    = numpy.mean(FinalValues3)
Qu3FiducilRows = Quadrant3FiducialRowStop - Quadrant3FiducialRowStart
Qu3Slope = (Qu3FinalVal - Qu3StartVal) / Qu3FiducilRows
# Quadrant 4:
Qu4StartVal    = numpy.mean(StartValues4)
Qu4FinalVal    = numpy.mean(FinalValues4)
Qu4FiducilRows = Quadrant4FiducialRowStop - Quadrant4FiducialRowStart
Qu4Slope = (Qu4FinalVal - Qu4StartVal) / Qu4FiducilRows
if(VerboseProcessing):
  print "Quadrant 1 average column slope = (" + "{:0.1f}".format(Qu1FinalVal) + " - " + "{:0.1f}".format(Qu1StartVal) + ") ADC Units / " + "{:0.1f}".format(Qu1FiducilRows) + " Rows = " + "{:0.1f}".format(Qu1Slope) + " ADC/Row"
  print "Quadrant 2 average column slope = (" + "{:0.1f}".format(Qu2FinalVal) + " - " + "{:0.1f}".format(Qu2StartVal) + ") ADC Units / " + "{:0.1f}".format(Qu2FiducilRows) + " Rows = " + "{:0.1f}".format(Qu2Slope) + " ADC/Row"
  print "Quadrant 3 average column slope = (" + "{:0.1f}".format(Qu3FinalVal) + " - " + "{:0.1f}".format(Qu3StartVal) + ") ADC Units / " + "{:0.1f}".format(Qu3FiducilRows) + " Rows = " + "{:0.1f}".format(Qu3Slope) + " ADC/Row"
  print "Quadrant 4 average column slope = (" + "{:0.1f}".format(Qu4FinalVal) + " - " + "{:0.1f}".format(Qu4StartVal) + ") ADC Units / " + "{:0.1f}".format(Qu4FiducilRows) + " Rows = " + "{:0.1f}".format(Qu4Slope) + " ADC/Row"

# Now Loop over the pixel values in the image and overscan regions and put them into a histogram.
import ROOT
import RootPlotLibs
import PythonTools
ROOT.gROOT.Reset()
ROOT.gROOT.ProcessLine(".L ./CompiledTools.C+")
PVBinWidth = 20.
PVIncr = 1.
# Quadrant 1:
# Create a histogram object for the pixel values
Qu1PVMin = numpy.round(min(CCDPixelValues1), 0)
while((Qu1PVMin % PVBinWidth) != (0.5 * PVBinWidth)):
  Qu1PVMin -= PVIncr
Qu1PVMax = numpy.round(max(CCDPixelValues1), 0)
while((Qu1PVMax % PVBinWidth) != (0.5 * PVBinWidth)):
  Qu1PVMax += PVIncr
nQu1PVBins = int((Qu1PVMax - Qu1PVMin) / PVBinWidth)
Qu1PVHisto = PythonTools.MakePixValHisto("Qu1PVHisto", "Pixel Values for Quadrant 1", nQu1PVBins, Qu1PVMin, Qu1PVMax, ROOT.kBlack)
Qu1PVHisto.GetXaxis().SetTitle("Quadrant 1 Pixel Values")
# Fill the histogram
for pv in CCDPixelValues1:
  Qu1PVHisto.Fill(pv)
# Quadrant 2:
# Create a histogram object for the pixel values
Qu2PVMin = numpy.round(min(CCDPixelValues2), 0)
while((Qu2PVMin % PVBinWidth) != (0.5 * PVBinWidth)):
  Qu2PVMin -= PVIncr
Qu2PVMax = numpy.round(max(CCDPixelValues2), 0)
while((Qu2PVMax % PVBinWidth) != (0.5 * PVBinWidth)):
  Qu2PVMax += PVIncr
nQu2PVBins = int((Qu2PVMax - Qu2PVMin) / PVBinWidth)
Qu2PVHisto = PythonTools.MakePixValHisto("Qu2PVHisto", "Pixel Values for Quadrant 2", nQu2PVBins, Qu2PVMin, Qu2PVMax, ROOT.kRed)
Qu2PVHisto.GetXaxis().SetTitle("Quadrant 2 Pixel Values")
# Fill the histogram
for pv in CCDPixelValues2:
  Qu2PVHisto.Fill(pv)
# Quadrant 3:
# Create a histogram object for the pixel values
Qu3PVMin = numpy.round(min(CCDPixelValues3), 0)
while((Qu3PVMin % PVBinWidth) != (0.5 * PVBinWidth)):
  Qu3PVMin -= PVIncr
Qu3PVMax = numpy.round(max(CCDPixelValues3), 0)
while((Qu3PVMax % PVBinWidth) != (0.5 * PVBinWidth)):
  Qu3PVMax += PVIncr
nQu3PVBins = int((Qu3PVMax - Qu3PVMin) / PVBinWidth)
Qu3PVHisto = PythonTools.MakePixValHisto("Qu3PVHisto", "Pixel Values for Quadrant 3", nQu3PVBins, Qu3PVMin, Qu3PVMax, ROOT.kGreen - 1)
Qu3PVHisto.GetXaxis().SetTitle("Quadrant 3 Pixel Values")
# Fill the histogram
for pv in CCDPixelValues3:
  Qu3PVHisto.Fill(pv)
# Quadrant 4:
# Create a histogram object for the pixel values
Qu4PVMin = numpy.round(min(CCDPixelValues4), 0)
while((Qu4PVMin % PVBinWidth) != (0.5 * PVBinWidth)):
  Qu4PVMin -= PVIncr
Qu4PVMax = numpy.round(max(CCDPixelValues4), 0)
while((Qu4PVMax % PVBinWidth) != (0.5 * PVBinWidth)):
  Qu4PVMax += PVIncr
nQu4PVBins = int((Qu4PVMax - Qu4PVMin) / PVBinWidth)
Qu4PVHisto = PythonTools.MakePixValHisto("Qu4PVHisto", "Pixel Values for Quadrant 4", nQu4PVBins, Qu4PVMin, Qu4PVMax, ROOT.kBlue)
Qu4PVHisto.GetXaxis().SetTitle("Quadrant 4 Pixel Values")
# Fill the histogram
for pv in CCDPixelValues4:
  Qu4PVHisto.Fill(pv)
# Overscan 1:
# Create a histogram object for the pixel values
OS1PVMin = numpy.round(min(VOSPixelValues1), 0)
while((OS1PVMin % PVBinWidth) != (0.5 * PVBinWidth)):
  OS1PVMin -= PVIncr
OS1PVMax = numpy.round(max(VOSPixelValues1), 0)
while((OS1PVMax % PVBinWidth) != (0.5 * PVBinWidth)):
  OS1PVMax += PVIncr
nOS1PVBins = int((OS1PVMax - OS1PVMin) / PVBinWidth)
OS1PVHisto = PythonTools.MakePixValHisto("OS1PVHisto", "Pixel Values for Overscan 1", nOS1PVBins, OS1PVMin, OS1PVMax, ROOT.kBlack)
OS1PVHisto.GetXaxis().SetTitle("Overscan 1 Pixel Values")
# Fill the histogram
for pv in VOSPixelValues1:
  OS1PVHisto.Fill(pv)
# Overscan 2:
# Create a histogram object for the pixel values
OS2PVMin = numpy.round(min(VOSPixelValues2), 0)
while((OS2PVMin % PVBinWidth) != (0.5 * PVBinWidth)):
  OS2PVMin -= PVIncr
OS2PVMax = numpy.round(max(VOSPixelValues2), 0)
while((OS2PVMax % PVBinWidth) != (0.5 * PVBinWidth)):
  OS2PVMax += PVIncr
nOS2PVBins = int((OS2PVMax - OS2PVMin) / PVBinWidth)
OS2PVHisto = PythonTools.MakePixValHisto("OS2PVHisto", "Pixel Values for Overscan 2", nOS2PVBins, OS2PVMin, OS2PVMax, ROOT.kRed)
OS2PVHisto.GetXaxis().SetTitle("Overscan 2 Pixel Values")
# Fill the histogram
for pv in VOSPixelValues2:
  OS2PVHisto.Fill(pv)
# Overscan 3:
# Create a histogram object for the pixel values
OS3PVMin = numpy.round(min(VOSPixelValues3), 0)
while((OS3PVMin % PVBinWidth) != (0.5 * PVBinWidth)):
  OS3PVMin -= PVIncr
OS3PVMax = numpy.round(max(VOSPixelValues3), 0)
while((OS3PVMax % PVBinWidth) != (0.5 * PVBinWidth)):
  OS3PVMax += PVIncr
nOS3PVBins = int((OS3PVMax - OS3PVMin) / PVBinWidth)
OS3PVHisto = PythonTools.MakePixValHisto("OS3PVHisto", "Pixel Values for Overscan 3", nOS3PVBins, OS3PVMin, OS3PVMax, ROOT.kGreen - 1)
OS3PVHisto.GetXaxis().SetTitle("Overscan 3 Pixel Values")
# Fill the histogram
for pv in VOSPixelValues3:
  OS3PVHisto.Fill(pv)
# Overscan 4:
# Create a histogram object for the pixel values
OS4PVMin = numpy.round(min(VOSPixelValues4), 0)
while((OS4PVMin % PVBinWidth) != (0.5 * PVBinWidth)):
  OS4PVMin -= PVIncr
OS4PVMax = numpy.round(max(VOSPixelValues4), 0)
while((OS4PVMax % PVBinWidth) != (0.5 * PVBinWidth)):
  OS4PVMax += PVIncr
nOS4PVBins = int((OS4PVMax - OS4PVMin) / PVBinWidth)
OS4PVHisto = PythonTools.MakePixValHisto("OS4PVHisto", "Pixel Values for Overscan 4", nOS4PVBins, OS4PVMin, OS4PVMax, ROOT.kBlue)
OS4PVHisto.GetXaxis().SetTitle("Overscan 4 Pixel Values")
# Fill the histogram
for pv in VOSPixelValues4:
  OS4PVHisto.Fill(pv)
# Draw all these histograms we just made.
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.08)
aPad.SetRightMargin(0.01)
aPad.SetBottomMargin(0.08)
aPad.Draw()
aPad.cd()
for plot in [Qu1PVHisto, Qu2PVHisto, Qu3PVHisto, Qu4PVHisto, OS1PVHisto, OS2PVHisto, OS3PVHisto, OS4PVHisto]:
  plot.Draw()
  aCanvas.Update()
  aCanvas.SaveAs(OutputDir + "/" + InputFilePath.split("/")[-1].replace("fits", plot.GetName() + ".pdf"))
# And write the to a root file...
aRootFile = ROOT.TFile(OutputDir + "/" + InputFilePath.split("/")[-1].replace("fits", "PVHistos" + ".root"), "recreate")
for plot in [Qu1PVHisto, Qu2PVHisto, Qu3PVHisto, Qu4PVHisto, OS1PVHisto, OS2PVHisto, OS3PVHisto, OS4PVHisto]:
  plot.Write()
aRootFile.Close()

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
