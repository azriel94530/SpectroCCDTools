#!/usr/bin/python

####################################################################################################
# Open a FITS file and turn it into a ROOT TH2F object for quantitative analysis.  Also make       #
# projection histograms along the x and y axes.  Save all these new objects to a root file, and    #
# make some nice plots of each, saving them as pdfs.                                               #
####################################################################################################

# Header, import statements etc.
import time
import sys
import astropy.io.fits
import numpy

####################################
#  BEGIN MAIN BODY OF THE CODE!!!  #
####################################

# Get the start time of this calculation
StartTime = time.time()

# Set some flags for how verbose our input and output are going to be.
Debugging = False
VerboseProcessing = True

if(len(sys.argv) != 2):
	print "Usage: python Fits2TH2F.py path/to/fits/image"
	exit()

# Pull in the path to the FITS file we're going to look at
InputFilePath = sys.argv[1]
if(VerboseProcessing): 
	print "\tReading in: '" + InputFilePath + "' for analysis."
	print "\tWriting output to", InputFilePath.replace("fits", "png"), "and", InputFilePath.replace("fits", "root") + "."

# Use astropy to open up the fits file we're after.
thisImage = astropy.io.fits.open(InputFilePath)
if(Debugging): print thisImage.info()

# Extract the dimensions of this fits image from the header information
nPixelsX = thisImage[0].header['NAXIS1']
nPixelsY = thisImage[0].header['NAXIS2']
nPixels = nPixelsX * nPixelsY

# Read the pixel dimensions out of the fits header.
lPixelX = thisImage[0].header['PXLDIM1']
lPixelY = thisImage[0].header['PXLDIM2']

# Now calculate the CCD dimensions...
lCCDX = nPixelsX * lPixelX
lCCDY = nPixelsY * lPixelY
if(VerboseProcessing): print "\t" + InputFilePath, "is", nPixelsX, "x", nPixelsY, "pixels (""{:0.0f}".format(lCCDX)  + " mm x " + "{:0.0f}".format(lCCDY) + " mm)."

# Start up all the ROOT stuff now that we're done reading in fits images...
import ROOT
import RootPlotLibs
ROOT.gROOT.Reset()
ROOT.gROOT.ProcessLine(".L ./CompiledTools.C+")

# Create a ROOT TH2F file to hold the fits image data.
xLo = -0.5 * lPixelX
xHi = lCCDX - xLo
yLo = -0.5 * lPixelY
yHi = lCCDY - yLo
thatHistogram = ROOT.TH2F("thatHistogram", "Histogram of " + InputFilePath, nPixelsX,xLo,xHi, nPixelsY,yLo,yHi)
thatHistogram.GetXaxis().SetTitle("x Position [mm]")
thatHistogram.GetXaxis().SetTitleOffset(1.1)
thatHistogram.GetYaxis().SetTitle("y Position [mm]")
thatHistogram.GetYaxis().SetTitleOffset(0.5)

# Step over all the pixels in the fits image and put their content in the corresponding bin in the
# TH2F.  While we're at it, calculate the mean and RMS of the pixel values.
MeanPixVal   = 0.
MeanPixValSq = 0.
iPixel = 0
for binX in range(nPixelsX):
	for binY in range(nPixelsY):
		thisPixelValue = thisImage[0].data[binY][binX]
		MeanPixVal += (thisPixelValue / float(nPixels))
		MeanPixValSq += ((thisPixelValue**2.) / float(nPixels))
		iPixel += 1
		thatBin = thatHistogram.FindBin(float(binX) * lPixelX, float(binY) * lPixelY)
		if(Debugging): print "Writing value:", thisPixelValue, "to bin number:", thatBin, "(position:", binX, "x", str(binY) + ")"
		thatHistogram.SetBinContent(binX, binY, thisPixelValue)
		if((nPixels >= 100) and (iPixel % int(nPixels / 100) == 0)):
			ROOT.StatusBar(iPixel, nPixels, int(nPixels / 100))
print
# Now that we have the mean of both the pixel value and its square, calculate the RMS.
RMSPixelVal = numpy.sqrt(MeanPixValSq - (MeanPixVal**2.))
if(VerboseProcessing): print "Mean pixel value: " + "{:0.1}".format(MeanPixVal) + " +/- " + "{:0.1f}".format(RMSPixelVal)
# Set the Z axis range on the histogram so that the contrast doesn't look terrible.
DisplayMin = MeanPixVal - RMSPixelVal
DisplayMax = MeanPixVal + RMSPixelVal
if(VerboseProcessing): print "\tSetting Z range:", DisplayMin, "to", str(DisplayMax) + "."
thatHistogram.GetZaxis().SetRangeUser(DisplayMin, DisplayMax)

# Get ready to plot all the things and save the plot as a png.
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.Draw()
aPad.cd()
thatHistogram.Draw("colz")
aCanvas.Update()
aCanvas.SaveAs(InputFilePath.replace("fits", "png"))

# Now make projections of thatHistogram along both the x and y axes.
aPad.SetLeftMargin(0.06)
aPad.SetRightMargin(0.01)
thatHistogramXproj = thatHistogram.ProjectionX("thatHistogramXproj", 0,nPixelsX, "o")
thatHistogramXproj.SetTitle("X Projection " + thatHistogram.GetTitle())
thatHistogramXproj.GetYaxis().SetTitle("Counts per " + "{:0.0f}".format(lPixelX * 1000.) + " #mum bin")
thatHistogramXproj.GetYaxis().SetTitleOffset(0.8)
thatHistogramXproj.Draw()
aCanvas.Update()
aCanvas.SaveAs(InputFilePath.replace(".fits", ".Xproj.png"))
thatHistogramYproj = thatHistogram.ProjectionY("thatHistogramYproj", 0,nPixelsY, "o")
thatHistogramYproj.SetTitle("Y Projection " + thatHistogram.GetTitle())
thatHistogramYproj.GetXaxis().SetTitleOffset(thatHistogramXproj.GetXaxis().GetTitleOffset())
thatHistogramYproj.GetYaxis().SetTitle("Counts per " + "{:0.0f}".format(lPixelY * 1000.) + " #mum bin")
thatHistogramYproj.GetYaxis().SetTitleOffset(0.8)
thatHistogramYproj.Draw()
aCanvas.Update()
aCanvas.SaveAs(InputFilePath.replace(".fits", ".Yproj.png"))
# Now save the TH2F to its own root file...
aRootFile = ROOT.TFile(InputFilePath.replace("fits", "root"), "recreate")
thatHistogram.Write()
thatHistogramXproj.Write()
thatHistogramYproj.Write()
aRootFile.Close()
# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
