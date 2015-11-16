#!/usr/bin/python

####################################################################################################
# This script is going to take the four x ray images from 2015-08-03 and pick out the hit pixels   #
# by compiling a list of pixels with higher values than all of their nearest neighbors.  We then   #
# create a 2D histogram for just the x ray hit pixels and the surrounding ones.  This will allow   #
# us to stack lots of hit pixels on top of one another to see if we can estimate our point spread  #
# function in both the 5 and 45 um directions.                                                     #
####################################################################################################

# Header, import statements etc.
import time
import sys
import numpy
import array
import ROOT
sys.path.append("../../")
import RootPlotLibs
import PythonTools

def GetStackedHitHisto(halfnpixels_x, halfnpixels_y):
  lPixelX =  5. #[um]
  lPixelY = 45. #[um]
  # Create a ROOT TH2F file to hold the fits image data.
  xLo = -1. * (0.5 + float(halfnpixels_x)) * lPixelX
  xHi =       (0.5 + float(halfnpixels_x)) * lPixelX
  yLo = -1. * (0.5 + float(halfnpixels_y)) * lPixelY
  yHi =       (0.5 + float(halfnpixels_y)) * lPixelY
  StackedHitHisto = ROOT.TH2D("StackedHitHisto", "Stacked Image of X Ray Hits", 
                              (2 * halfnpixels_x) + 1, xLo, xHi, 
                              (2 * halfnpixels_y) + 1, yLo, yHi)
  StackedHitHisto.GetXaxis().SetTitle("x Distance from Hit Pixel [#mum]")
  StackedHitHisto.GetXaxis().SetTitleOffset(1.0)
  StackedHitHisto.GetYaxis().SetTitle("y Distance from Hit Pixel [#mum]")
  StackedHitHisto.GetYaxis().SetTitleOffset(0.8)
  return StackedHitHisto


####################################
#  BEGIN MAIN BODY OF THE CODE!!!  #
####################################

# Get the start time of this calculation
StartTime = time.time()

# ROOT housekeeping...
ROOT.gROOT.Reset()
ROOT.gROOT.ProcessLine(".L ../../CompiledTools.C+")

# Set some flags for how verbose our input and output are going to be.
Debugging = False
VerboseProcessing = True
PlotImageHisto = False
PlotStackedImageHisto = True

# Pull in the path to the root files we're going to look at
InputFilePath = "/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-08-03/noClearXray1/noClearXray1_UnShuf.root"
if(VerboseProcessing): 
  print "\tReading in: '" + InputFilePath + "' for analysis."

# Crack open the file, get the pixel value histogram...
InputFile = ROOT.TFile(InputFilePath)
ImageHisto = InputFile.Get("thatHistogram")

# Set up the range over which we are going to do the analysis.
xLo =  0.5
xHi = 12.
yLo =  2.
yHi = 26.

# If the flag is set, go ahead and plot this thing now...
if(PlotImageHisto):
  aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
  aCanvas.Draw()
  aCanvas.cd()
  aPad.SetLeftMargin(0.05)
  aPad.SetRightMargin(0.12)
  aPad.SetBottomMargin(0.08)
  aPad.SetLogy(0)
  aPad.Draw()
  aPad.cd()
  ImageHisto.GetXaxis().SetRangeUser(xLo, xHi)
  ImageHisto.GetYaxis().SetRangeUser(yLo, yHi)
  ImageHisto.Draw("colz")
  aCanvas.Update()
  aCanvas.SaveAs(InputFilePath.replace(".root", ".TH2D.png"))
  aCanvas.Clear()
  del aPad
  del aCanvas

# Now, we need to loop over all the bins in the TH2D and pick out the x ray hit clusters.  Since
# the pixels are nine times bigger in the y direction than in the y direction, charge is more
# likely to be shared between neighboring pixels in the x direction.  That means that we're going
# to step over *rows* pixels in the x direction for each y position, and find local maxima.
xBinsToAnalyze = range(ImageHisto.GetXaxis().FindBin(xLo), ImageHisto.GetXaxis().FindBin(xHi) + 1)
yBinsToAnalyze = range(ImageHisto.GetYaxis().FindBin(yLo), ImageHisto.GetYaxis().FindBin(yHi) + 1)
NumberOfPixelsToAnalyze = len(xBinsToAnalyze) * len(yBinsToAnalyze)
if(Debugging):
  print xBinsToAnalyze
  print yBinsToAnalyze
# We would also like to track the number of pixels that above threshold (some number of RMS), and
# therefore are candidate x ray interaction sites in each row of pixels.
ThresholdInRMS = 80.
# And here is where we will store all the bins above threshold and their values.
xBinsAboveThreshold = []
yBinsAboveThreshold = []
RowAvgData = []
RowRMSData = []
PixelValuesAboveThr = []
iYBin = -1
# Loop over the bins in the y direction...
if(VerboseProcessing):
  print "\n\tCalculating threshold in each row and finding the pixels above it..."
for yBin in yBinsToAnalyze:
  iYBin += 1
  if((len(yBinsToAnalyze) >= 100) and (iYBin % int(len(yBinsToAnalyze) / 100) == 0)):
    ROOT.StatusBar(iYBin, len(yBinsToAnalyze), len(yBinsToAnalyze) / 100)
  RowAvg   = 0.
  RowSqAvg = 0.
  # Loop over the pixels in the x direction at this value of y...
  for xBin in xBinsToAnalyze:
    thisPixVal = ImageHisto.GetBinContent(xBin, yBin)
    RowAvg   += thisPixVal / NumberOfPixelsToAnalyze
    RowSqAvg += (ImageHisto.GetBinContent(xBin, yBin)**2.) / NumberOfPixelsToAnalyze
  iYBin += 1
  RowRMS = (RowSqAvg - (RowAvg**2.))**0.5
  RowAvgData.append(RowAvg)
  RowRMSData.append(RowRMS)
  # Now that we know the mean and RMS, loop back over this row, count the number of departures
  # above threshold, and track which bins do so.
  for xBin in xBinsToAnalyze:
    thisBinVal = ImageHisto.GetBinContent(xBin, yBin)
    if(thisBinVal > (ThresholdInRMS * RowRMS)):
      xBinsAboveThreshold.append(xBin)
      yBinsAboveThreshold.append(yBin)
      PixelValuesAboveThr.append(thisBinVal)
print 
if(VerboseProcessing): 
  print "\tAverage pixel value:", numpy.mean(RowAvgData), "+/-", numpy.mean(RowRMSData)
  print "\tTotal of", len(PixelValuesAboveThr), "pixels were above threshold."

# Find the local maximum bins in this image.
if(VerboseProcessing):
  print "\n\tIdentifying which pixels above threshold are local maxima..."
xLMCheckRange = 2 # Number of bins to check above and below each threshold departure to see if it
yLMCheckRange = 1 # is a local maximum in x and y.
LocalMaxBinsX = []
LocalMaxBinsY = []
LocalMaxPixels = []
# Loop over the pixels we just identified as threshold excursions and see if they are local maxima.
for i in range(len(PixelValuesAboveThr)):
  if((len(PixelValuesAboveThr) >= 100) and (i % int(len(PixelValuesAboveThr) / 100) == 0)):
    ROOT.StatusBar(i, len(PixelValuesAboveThr), len(PixelValuesAboveThr) / 100)
  LocalMax = True
  thisPixVal = ImageHisto.GetBinContent(xBinsAboveThreshold[i], yBinsAboveThreshold[i])
  NeighboringPixVals = []
  #Loop over the neighboring pixels and capture their numerical values.
  for iY in range(-1 * yLMCheckRange, yLMCheckRange + 1):
    for iX in range(-1 * xLMCheckRange, xLMCheckRange + 1):
      #print thisPixVal, xBinsAboveThreshold[i] + iX, yBinsAboveThreshold[i] + iY, ImageHisto.GetBinContent(xBinsAboveThreshold[i] + iX, yBinsAboveThreshold[i] + iY)
      if((iX != 0) or (iY != 0)): 
        NeighboringPixVals.append(ImageHisto.GetBinContent(xBinsAboveThreshold[i] + iX, yBinsAboveThreshold[i] + iY))
  # If the current pixel value is less than any of its neighbors, set LocalMax to False
  for npv in NeighboringPixVals:
    if(thisPixVal < npv): LocalMax = False
  # If this pixel is a local maximum, then save this pair of x and y bins.
  if(LocalMax):
    LocalMaxBinsX.append(xBinsAboveThreshold[i])
    LocalMaxBinsY.append(yBinsAboveThreshold[i])
    LocalMaxPixels.append(thisPixVal)
print 
if(VerboseProcessing):
  print "\tTotal of", len(LocalMaxBinsX), "pixels were found to be local maxima."
  print "\tSum of the local maximum pixels is:", numpy.sum(LocalMaxPixels)

# Make the stacked image histograms:
HalfNpixels_X = 4
HalfNpixels_Y = 2
StackedHitHisto1 = GetStackedHitHisto(HalfNpixels_X, HalfNpixels_Y)
lPixelX = StackedHitHisto1.GetXaxis().GetBinCenter(2) - StackedHitHisto1.GetXaxis().GetBinCenter(1)
lPixelY = StackedHitHisto1.GetYaxis().GetBinCenter(2) - StackedHitHisto1.GetYaxis().GetBinCenter(1)
# and now fill them...
for i in range(len(LocalMaxBinsX)):
  for iY in range(-1 * yLMCheckRange, yLMCheckRange + 1):
    for iX in range(-1 * xLMCheckRange, xLMCheckRange + 1):
      thisStackedX = float(iX) * lPixelX
      thisStackedY = float(iY) * lPixelY
      thisImageX = ImageHisto.GetXaxis().GetBinCenter(LocalMaxBinsX[i] + iX)
      thisImageY = ImageHisto.GetYaxis().GetBinCenter(LocalMaxBinsY[i] + iY)
      thisImageBin = ImageHisto.FindBin(thisImageX, thisImageY)
      thisBinContent = ImageHisto.GetBinContent(thisImageBin)
      StackedHitHisto1.Fill(thisStackedX, thisStackedY, thisBinContent)
if(VerboseProcessing):
  print "\tThe central bin of the stacked histogram has", StackedHitHisto1.GetBinContent(StackedHitHisto1.FindBin(0., 0.)), "counts."
  print "\tThis should be the same as the sum of the local maximum pixels:", numpy.sum(LocalMaxPixels)

# If the flag is set, go ahead and plot this thing now...
if(PlotStackedImageHisto):
  aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
  aCanvas.Draw()
  aCanvas.cd()
  aPad.SetLeftMargin(0.06)
  aPad.SetRightMargin(0.12)
  aPad.SetBottomMargin(0.08)
  aPad.SetLogy(0)
  aPad.Draw()
  aPad.cd()
  StackedHitHisto1.Draw("colz")
  aCanvas.Update()
  aCanvas.SaveAs(InputFilePath.replace(".root", ".StackedXRays.png"))
  aCanvas.Clear()
  del aPad
  del aCanvas

# Now that we've got the stacked x ray hit image, let's sum over the y bins for each bin in the
# x direction.
XValues = []
XProfile = []
for xBin in range(1, StackedHitHisto1.GetXaxis().GetNbins() + 1):
  XValues.append(StackedHitHisto1.GetXaxis().GetBinCenter(xBin))
  thisProfileValue = 0.
  for yBin in range(1, StackedHitHisto1.GetYaxis().GetNbins() + 1):
    thisYValue = StackedHitHisto1.GetYaxis().GetBinCenter(yBin)
    thisBin = StackedHitHisto1.FindBin(XValues[-1], thisYValue)
    thisProfileValue += StackedHitHisto1.GetBinContent(thisBin)
  XProfile.append(thisProfileValue)
XProfileGraph = ROOT.TGraph(len(XValues), array.array("f", XValues), array.array("f", XProfile))
XProfileGraph.SetName("XProfileGraph")
XProfileGraph.SetMarkerStyle(20)
XProfileGraph.SetMarkerSize(3)
XProfileGraph.SetMarkerColor(ROOT.kBlack)
XProfileGraph.GetXaxis().SetTitle(StackedHitHisto1.GetXaxis().GetTitle())
XProfileGraph.GetXaxis().SetTitleOffset(StackedHitHisto1.GetXaxis().GetTitleOffset())

# Now let's plot the profile and fit a Gaussian to it...
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.08)
aPad.SetRightMargin(0.015)
aPad.SetBottomMargin(0.09)
aPad.SetLogy(0)
aPad.Draw()
aPad.cd()
XProfileGraph.Draw("alp")
#XProfileFitModel = PythonTools.GetOneGausFitModel("XProfileFitModel", XProfileGraph, 0., 20.)
#XProfileFitModel.FixParameter(0, 0.)
#XProfileFitModel.SetParLimits(2, -3., 3.)
#XProfileGraph.Fit(XProfileFitModel, "WEM", "", XValues[0], XValues[-1])
aCanvas.SaveAs("./" + XProfileGraph.GetName() + ".pdf")

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
