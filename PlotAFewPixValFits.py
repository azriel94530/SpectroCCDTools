#!/usr/bin/python

####################################################################################################
# Open a FITS file and plot the fit to some of its column data...                                  #
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

if(len(sys.argv) != 4):
  print "Usage: [python] Fits2TH2F.py path/to/fits/image StartingPixelColumn NumberOfColumnsToPlot"
  exit()

# Pull in the path to the FITS file we're going to look at
InputFilePath = sys.argv[1]
if(VerboseProcessing):
  print "\tReading in: '" + InputFilePath + "' for analysis."
  print "\tWriting output to", InputFilePath.replace("fits", "png"), "and", InputFilePath.replace("fits", "root") + "."

# And decide where and how many of it's columns we're going to fiddle with.
StartingPixelColumn   = int(sys.argv[2])
NumberOfColumnsToPlot = int(sys.argv[3])
if(VerboseProcessing): print "\tStarting with column", StartingPixelColumn, "and plotting a total of", NumberOfColumnsToPlot

# Use astropy to open up the fits file we're after.
thisImage = astropy.io.fits.open(InputFilePath)
if(Debugging): print thisImage.info()

# Extract the dimensions of this fits image from the header information
nPixelsX = thisImage[0].header['NAXIS1']
nPixelsY = thisImage[0].header['NAXIS2']
nPixels = nPixelsX * nPixelsY
if(VerboseProcessing): print "\tThis image is", nPixelsX, "by", nPixelsY, "pixels, for a total of", nPixels

# A little error checking here...
if((StartingPixelColumn < 0) or ((StartingPixelColumn + NumberOfColumnsToPlot) >= nPixelsX)):
  print "Check the limits of your pixel columns to plot.  They seem to be out of range..."
  exit()

# Read the pixel dimensions out of the fits header.
lPixelX = thisImage[0].header['PXLDIM1']
lPixelY = thisImage[0].header['PXLDIM2']

# Now calculate the CCD dimensions...
lCCDX = nPixelsX * lPixelX
lCCDY = nPixelsY * lPixelY
yLo = -0.5 * lPixelY
yHi = lCCDY - yLo
if(VerboseProcessing): print "\t" + InputFilePath, "is", nPixelsX, "x", nPixelsY, "pixels (""{:0.0f}".format(lCCDX)  + " mm x " + "{:0.0f}".format(lCCDY) + " mm)."

# Start up all the ROOT stuff now that we're done reading in fits images...
import ROOT
import RootPlotLibs
import PythonTools
ROOT.gROOT.Reset()
ROOT.gROOT.ProcessLine(".L ./CompiledTools.C+")

# Let's make a list to hold TGraph objects that will hold the column by column data that we're
# going to plot and fit to.
ColumnGraphs = []
MaxPixVal = 0
# Step over all the pixels in the fits image and put their content in the corresponding bin in the
# TH2F.
if(VerboseProcessing): print "\n\tReading in the individual columns for this image."
iPixel = 0
for binX in range(StartingPixelColumn, StartingPixelColumn + NumberOfColumnsToPlot):
  thisColumnData    = numpy.zeros(nPixelsY)
  thisColumnUnc     = numpy.zeros(nPixelsY)
  thisYPositionData = numpy.zeros(nPixelsY)
  thisYPositionUnc  = numpy.zeros(nPixelsY)
  for binY in range(nPixelsY):
    # Extract the current pixel value from the image, then save it along with the current 
    # y/column position to a pair of arrays for future background fits
    thisPixelValue = thisImage[0].data[binY][binX]
    if(thisPixelValue > MaxPixVal): MaxPixVal = thisPixelValue
    thisColumnData[binY] = thisPixelValue
    thisColumnUnc[binY]  = numpy.sqrt(thisPixelValue)
    thisYPositionData[binY] = yLo + (binY * lPixelY)
    thisYPositionUnc[binY] = 0.5 * lPixelY
    iPixel += 1
  thisColumnGraph = ROOT.TGraphErrors(nPixelsY, thisYPositionData, thisColumnData, thisYPositionUnc, thisColumnUnc)
  thisColumnGraph.SetMarkerStyle(20)
  thisColumnGraph.SetMarkerSize(1)
  if((len(ColumnGraphs) % 2) == 0):
    thisColumnGraph.SetMarkerColor(ROOT.kBlue)
    thisColumnGraph.SetLineColor(ROOT.kBlue)
  elif((len(ColumnGraphs) % 2) == 1):
    thisColumnGraph.SetMarkerColor(ROOT.kBlack)
    thisColumnGraph.SetLineColor(ROOT.kBlack)
  else:
    print "What???"
    exit()
  ColumnGraphs.append(thisColumnGraph)
print

# Construct a fit to the background for each column in the CCD.
if(VerboseProcessing): print "\n\tConstructing column-by-column background model."
ConstaCoefs = numpy.zeros(NumberOfColumnsToPlot)# To save the fit coefficients and uncertainties
ConstaCoErs = numpy.zeros(NumberOfColumnsToPlot)
LinearCoefs = numpy.zeros(NumberOfColumnsToPlot)
LinearCoErs = numpy.zeros(NumberOfColumnsToPlot)
QuadraCoefs = numpy.zeros(NumberOfColumnsToPlot)
QuadraCoErs = numpy.zeros(NumberOfColumnsToPlot)
ChiSqupNDFs = numpy.zeros(NumberOfColumnsToPlot)# To save the chi squared values
LinearGuess  = ROOT.TF1("LinearGuess",  "[0] + ([1] * x)",                 yLo, yHi)
QuadraticFit = ROOT.TF1("QuadraticFit", "[0] + ([1] * x) + ([2] * (x^2))", yLo, yHi)
EdgeBuffer = 25 #Number of pixels to cheat in from the edges since they are some times kind of wonky.
FitLo = ColumnGraphs[0].GetX()[EdgeBuffer]
FitHi = ColumnGraphs[0].GetX()[ColumnGraphs[0].GetN() - EdgeBuffer]
FracDiffThresh = 0.10 # Fractional deviation allowed to make it into the quadratic fit.
FracDiffCount = numpy.zeros(NumberOfColumnsToPlot)
iColumn = -1
for graph in ColumnGraphs:
  iColumn += 1
  # First just do a linear fit to get rid of outlying pixels
  Slope = (graph.GetY()[graph.GetN() - EdgeBuffer] - graph.GetY()[EdgeBuffer]) / (graph.GetX()[graph.GetN() - EdgeBuffer] - graph.GetX()[EdgeBuffer])
  Offset = graph.GetY()[EdgeBuffer] - (Slope * graph.GetX()[EdgeBuffer])
  LinearGuess.SetParameter(0, Offset)
  LinearGuess.SetParameter(1, Slope)
  if(Debugging): print "\t\tColumn number", iColumn
  graph.Fit("LinearGuess", "QN", "", FitLo, FitHi)
  # Step over the points in the graph and throw out points that deviate by more than FracDiffThresh. 
  for i in range(graph.GetN()):
    if(numpy.abs(graph.GetY()[i] - LinearGuess.Eval(graph.GetX()[i])) > numpy.abs(FracDiffThresh * graph.GetY()[i])):
      graph.GetX()[i] = -10.
      graph.GetY()[i] =  0.
      FracDiffCount[iColumn] += 1
  if(Debugging): print "\t\tThrowing out", FracDiffCount[iColumn], "pixels."
  QuadraticFit.SetParameter(0, LinearGuess.GetParameter(0))
  QuadraticFit.SetParameter(1, LinearGuess.GetParameter(1))
  QuadraticFit.SetParameter(2, 0.)
  graph.Fit("QuadraticFit", "QEMN", "", FitLo, FitHi)
  # Now save the fit function, its coefficients, and all the other stuff we want to keep track of.
  ConstaCoefs[iColumn] = QuadraticFit.GetParameter(0)
  ConstaCoErs[iColumn] = QuadraticFit.GetParError(0)
  LinearCoefs[iColumn] = QuadraticFit.GetParameter(1)
  LinearCoErs[iColumn] = QuadraticFit.GetParError(1)
  QuadraCoefs[iColumn] = QuadraticFit.GetParameter(2)
  QuadraCoErs[iColumn] = QuadraticFit.GetParError(2)
  ChiSqupNDFs[iColumn] = QuadraticFit.GetChisquare() / float(QuadraticFit.GetNDF())
print
if(VerboseProcessing): 
  print "\tWe just did", len(ConstaCoefs), "fits.  Saving the salient results..."
  print "\tCol.\tConst.\t\t\tLinear\t\tQuadratic"
  for i in range(len(ConstaCoefs)):
    print "\t", i, "\t" + "{:1.1f}".format(ConstaCoefs[i]) + " +/- " + "{:1.1f}".format(ConstaCoErs[i]) + "\t" + "{:1.1f}".format(LinearCoefs[i]) + " +/- " + "{:1.1f}".format(LinearCoErs[i]) + "\t" + "{:1.1f}".format(QuadraCoefs[i]) + " +/- " + "{:1.1f}".format(QuadraCoErs[i])

# Get ready to plot all the things and save them as a png.
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.08)
aPad.SetRightMargin(0.01)
aPad.Draw()
aPad.cd() 
CanvasSetup = ROOT.TH2D("CanvasSetup", "Column Data and Fits to It...", 1,yLo, yHi, 1,0.,1.1*MaxPixVal)
CanvasSetup.GetXaxis().SetTitle("Pixel Y Position [mm]")
CanvasSetup.GetYaxis().SetTitle("Pixel Value [ADC]")
for i in range(len(ColumnGraphs)):
  CanvasSetup.Draw()
  ColumnGraphs[i].Draw("samep")
  QuadraticFit.SetParameter(0, ConstaCoefs[i])
  QuadraticFit.SetParameter(1, LinearCoefs[i])
  QuadraticFit.SetParameter(2, QuadraCoefs[i])
  QuadraticFit.Draw("samel")
  aCanvas.Update()
  aCanvas.SaveAs(InputFilePath.replace(".fits", ".Col_" + str(StartingPixelColumn + i) + ".pdf"))

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
