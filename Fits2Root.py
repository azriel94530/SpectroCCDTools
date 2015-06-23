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
import array

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
thatHistogram.GetXaxis().SetTitleOffset(1.0)
thatHistogram.GetYaxis().SetTitle("y Position [mm]")
thatHistogram.GetYaxis().SetTitleOffset(0.7)

# Let's make a list to hold TGraph objects that will hold the column by column data used to
# subtract off the background.
ColumnGraphs = []

# Step over all the pixels in the fits image and put their content in the corresponding bin in the
# TH2F.
if(VerboseProcessing): print "\n\tReading in the individual columns for this image."
iPixel = 0
for binX in range(nPixelsX):
  thisColumnData    = numpy.zeros(nPixelsY)
  thisYPositionData = numpy.zeros(nPixelsY)
  for binY in range(nPixelsY):
    # Extract the current pixel value from the image, then save it along with the current 
    # y/column position to a pair of arrays for future background fits
    thisPixelValue = thisImage[0].data[binY][binX]
    thisColumnData[binY] = thisPixelValue
    thisYPositionData[binY] = yLo + (binY * lPixelY)
    iPixel += 1
    if((nPixels >= 100) and (iPixel % int(nPixels / 100) == 0)):
      ROOT.StatusBar(iPixel, nPixels, int(nPixels / 100))
  thisColumnGraph = ROOT.TGraph(nPixelsY, thisYPositionData, thisColumnData)
  #thisColumnGraph.SetMarkerStyle(20)
  #thisColumnGraph.SetMarkerSize(1)
  #thisColumnGraph.SetMarkerColor(ROOT.kBlue)
  ColumnGraphs.append(thisColumnGraph)
print

# Construct a fit to the background for each column in the CCD.
if(VerboseProcessing): print "\n\tConstructing column-by-column background model."
ColumnFits = []
LinearGuess  = ROOT.TF1("LinearGuess",  "[0] + ([1] * x)",                 yLo, yHi)
QuadraticFit = ROOT.TF1("QuadraticFit", "[0] + ([1] * x) + ([2] * (x^2))", yLo, yHi)
EdgeBuffer = 50 #Number of pixels to cheat in from the edges since they are some times kind of wonky.
FitLo = ColumnGraphs[0].GetX()[EdgeBuffer]
FitHi = ColumnGraphs[0].GetX()[ColumnGraphs[0].GetN() - EdgeBuffer]
FracDiffThresh = 0.01
FracDiffCount = []
iColumn = -1
for graph in ColumnGraphs:
  iColumn += 1
  if((nPixelsY >= 100) and (iColumn % int(nPixelsY / 100) == 0)):
      ROOT.StatusBar(iColumn, nPixelsY, int(nPixelsY / 100))
  Slope = (graph.GetY()[graph.GetN() - EdgeBuffer] - graph.GetY()[EdgeBuffer]) / (graph.GetX()[graph.GetN() - EdgeBuffer] - graph.GetX()[EdgeBuffer])
  Offset = graph.GetY()[EdgeBuffer] - (Slope * graph.GetX()[EdgeBuffer])
  LinearGuess.SetParameter(0, Offset)
  LinearGuess.SetParameter(1, Slope)
  if(Debugging): print "\t\tColumn number", iColumn
  graph.Fit("LinearGuess", "Q", "", FitLo, FitHi)
  FracDiffCount.append(0)
  for i in range(graph.GetN()):
    if((graph.GetY()[i] - LinearGuess.Eval(graph.GetX()[i])) > (FracDiffThresh * graph.GetY()[i])):
      graph.GetX()[i] = -10.
      graph.GetY()[i] =  0.
      FracDiffCount[-1] += 1
  if(Debugging): print "\t\tThrowing out", FracDiffCount[-1], "pixels."
  QuadraticFit.SetParameter(0, LinearGuess.GetParameter(0))
  QuadraticFit.SetParameter(1, LinearGuess.GetParameter(1))
  QuadraticFit.SetParameter(2, 0.)
  graph.Fit("QuadraticFit", "QEM", "", FitLo, FitHi)
  ColumnFits.append(QuadraticFit)
print
if(VerboseProcessing): print "\tWe just did", len(ColumnFits), "fits."

# And step over the image buffer one more time to histogram the backgruond corrected pixel values.
if(VerboseProcessing): print "\n\tMake a background corrected two-dimensional histogram of the image."
iPixel = 0
MeanPixVal   = 0.
MeanPixValSq = 0.
MinPixVal =  1.e12
MaxPixVal = -1.e12
for binX in range(nPixelsX):
  for binY in range(nPixelsY):
    thisPixelValue = thisImage[0].data[binY][binX] - ColumnFits[binX].Eval(thisYPositionData[binY])
    thatBin = thatHistogram.FindBin(float(binX) * lPixelX, float(binY) * lPixelY)
    if(Debugging): print "Writing value:", thisPixelValue, "to bin number:", thatBin, "(position:", binX, "x", str(binY) + ")"
    thatHistogram.SetBinContent(binX, binY, thisPixelValue)
    if(thisPixelValue < MinPixVal): MinPixVal = thisPixelValue
    if(thisPixelValue > MaxPixVal): MaxPixVal = thisPixelValue
    MeanPixVal += (thisPixelValue / float(nPixels))
    MeanPixValSq += ((thisPixelValue**2.) / float(nPixels))
    iPixel += 1
    if((nPixels >= 100) and (iPixel % int(nPixels / 100) == 0)):
      ROOT.StatusBar(iPixel, nPixels, int(nPixels / 100))
print
# Now that we have the mean of both the pixel value and its square, calculate the RMS.
RMSPixelVal = numpy.sqrt(MeanPixValSq - (MeanPixVal**2.))
if(VerboseProcessing):
  print "\tMean pixel value: " + "{:5.1}".format(MeanPixVal) + " +/- " + "{:5.1f}".format(RMSPixelVal)
  print "\tFull range was from " + "{:5.1}".format(MinPixVal) + " to " + "{:5.1f}".format(MaxPixVal)
# Set the Z axis range on the histogram so that the contrast doesn't look terrible.
DisplayMin = MeanPixVal - (2. * RMSPixelVal)
DisplayMax = MeanPixVal + (4. * RMSPixelVal)
if(VerboseProcessing): print "\tSetting Z range: " + "{:5.1}".format(DisplayMin) + " to " + "{:5.1}".format(DisplayMax)
thatHistogram.GetZaxis().SetRangeUser(DisplayMin, DisplayMax)

# Now that we know what the range of this histogram should be, build a background-corrected pixel
# value histogram for the whole chip.
if(VerboseProcessing): print "\n\tHistogram the background-corrected pixel values."
nPixValBins = 1000
PixValBinWidth = (MaxPixVal - MinPixVal) / float(nPixValBins)
YTitleOffset = 1.1
PixValHisto = ROOT.TH1D("PixValHisto", "Histogram of Background-Corrected Pixel Values Over Entire CCD", nPixValBins,MinPixVal,MaxPixVal)
PixValHisto.GetXaxis().SetTitle("Pixel Value [ADC Counts]")
PixValHisto.GetYaxis().SetTitle("Counts per " + "{:3.0f}".format(PixValBinWidth) + " ADC bin")
PixValHisto.GetYaxis().SetTitleOffset(YTitleOffset)
iPixel = 0
for binX in range(nPixelsX):
  for binY in range(nPixelsY):
    thisPixelValue = thisImage[0].data[binY][binX] - ColumnFits[binX].Eval(thisYPositionData[binY])
    PixValHisto.Fill(thisPixelValue)
    iPixel += 1
    if((nPixels >= 100) and (iPixel % int(nPixels / 100) == 0)):
      ROOT.StatusBar(iPixel, nPixels, int(nPixels / 100))
print

# Get ready to plot all the things and save them as a png.
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.05)
aPad.SetBottomMargin(0.08)
aPad.Draw()
aPad.cd()
thatHistogram.Draw("colz")
aCanvas.Update()
aCanvas.SaveAs(InputFilePath.replace("fits", "png"))

# Now make projections of thatHistogram along both the x and y axes.
aPad.SetLeftMargin(0.08)
aPad.SetRightMargin(0.01)
thatHistogramXproj = thatHistogram.ProjectionX("thatHistogramXproj", 0,nPixelsX, "o")
thatHistogramXproj.SetTitle("X Projection " + thatHistogram.GetTitle())
thatHistogramXproj.GetYaxis().SetTitle("Counts per " + "{:0.0f}".format(lPixelX * 1000.) + " #mum bin")
thatHistogramXproj.GetYaxis().SetTitleOffset(YTitleOffset)
thatHistogramXproj.Draw()
aCanvas.Update()
aCanvas.SaveAs(InputFilePath.replace(".fits", ".Xproj.png"))
thatHistogramYproj = thatHistogram.ProjectionY("thatHistogramYproj", 0,nPixelsY, "o")
thatHistogramYproj.SetTitle("Y Projection " + thatHistogram.GetTitle())
thatHistogramYproj.GetXaxis().SetTitleOffset(thatHistogramXproj.GetXaxis().GetTitleOffset())
thatHistogramYproj.GetYaxis().SetTitle("Counts per " + "{:0.0f}".format(lPixelY * 1000.) + " #mum bin")
thatHistogramYproj.GetYaxis().SetTitleOffset(YTitleOffset)
thatHistogramYproj.Draw()
aCanvas.Update()
aCanvas.SaveAs(InputFilePath.replace(".fits", ".Yproj.png"))

# Draw the pixel value histogram.
aPad.SetLogy(1)
PixValHisto.Draw()
aCanvas.Update()
aCanvas.SaveAs(InputFilePath.replace(".fits", ".PixValHisto.png"))

# Now save the TH2F to its own root file...
aRootFile = ROOT.TFile(InputFilePath.replace("fits", "root"), "recreate")
thatHistogram.Write()
thatHistogramXproj.Write()
thatHistogramYproj.Write()
PixValHisto.Write()
aRootFile.Close()
# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
