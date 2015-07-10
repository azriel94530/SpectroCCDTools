#!/usr/bin/python

####################################################################################################
# Open up the 2D histogram of a fits image created by Fits2Root.py, and histogram the background   #
# corrected pixel values.                                                                          #
####################################################################################################

# Header, import statements etc.
import time
import sys
import ROOT
import RootPlotLibs
import PythonTools
import numpy

####################################
#  BEGIN MAIN BODY OF THE CODE!!!  #
####################################

# Get the start time of this calculation
StartTime = time.time()

# Get ROOT going and load a useful function or two.
ROOT.gROOT.Reset()
ROOT.gROOT.ProcessLine(".L ./CompiledTools.C+")

# Set some flags for how verbose our input and output are going to be.
Debugging = False
VerboseProcessing = True

# Figure out exactly what we're doing based on what get's passed to this thing as an argument.
if(len(sys.argv) == 2):
  NoSpecifiedRange = True
  NoOutputNameSpecified = True
  InputFilePath = sys.argv[1]
  print "\tReading in: '" + InputFilePath + "' for analysis."
elif(len(sys.argv) == 6):
  NoSpecifiedRange = False
  NoOutputNameSpecified = True
  InputFilePath = sys.argv[1]
  xLo = float(sys.argv[2])
  xHi = float(sys.argv[3])
  yLo = float(sys.argv[4])
  yHi = float(sys.argv[5])
  print "\tReading in: '" + InputFilePath + "' for analysis."
  print "\tZooming in on: ", xLo, "< x <", xHi, "and", yLo, "< y <", yHi, "mm."
elif(len(sys.argv) == 7):
  NoSpecifiedRange = False
  NoOutputNameSpecified = False
  InputFilePath = sys.argv[1]
  xLo = float(sys.argv[2])
  xHi = float(sys.argv[3])
  yLo = float(sys.argv[4])
  yHi = float(sys.argv[5])
  OutputTag = sys.argv[6]
  print "\tReading in: '" + InputFilePath + "' for analysis."
  print "\tZooming in on: ", xLo, "< x <", xHi, "and", yLo, "< y <", yHi, "mm."
  print "\tTagging output with the string, \'" + OutputTag + "\'"
else:
  print "Usage: [python] AnalyzeNoise.py path/to/fits/root/file [xRangeLo xRangeHi yRangeLo yRangeHi OutputIdentifierString]"
  exit()
# If you haven't already done so, have the user input a string to tag the output of this particular
# pixel value histogram.
if(NoOutputNameSpecified):
  OutputTag = input("\tHow about a string (IN QUOTES!!!) to tag the output of this analysis? ")
  print "\tTagging output with the string, \'" + OutputTag + "\'"

# Crack open the root file, get the 2D histogram, draw it, and zoom in on the region of interest...
InputFile = ROOT.TFile(InputFilePath)
ImageHisto = InputFile.Get("thatHistogram")
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.05)
aPad.SetBottomMargin(0.08)
aPad.Draw()
aPad.cd()
if(NoSpecifiedRange):
  ImageHisto.Draw("colz")
  aCanvas.Update()
  xLo = float(input("\tx Range Low?  "))
  xHi = float(input("\tx Range High? "))
  yLo = float(input("\ty Range Low?  "))
  yHi = float(input("\ty Range High? "))
  print "\tZooming in on: ", xLo, "< x <", xHi, "and", yLo, "< y <", yHi, "mm."
ImageHisto.GetXaxis().SetRangeUser(xLo, xHi)
ImageHisto.GetYaxis().SetRangeUser(yLo, yHi)
ImageHisto.GetZaxis().UnZoom()
ImageHisto.Draw("colz")
aCanvas.Update()
aCanvas.SaveAs(InputFilePath.replace(".root", "." + OutputTag + ".png"))
#raw_input()

# Pull in the list of bins in both X and Y we're going to look at.
Xbins = range(ImageHisto.GetXaxis().FindBin(xLo), ImageHisto.GetXaxis().FindBin(xHi))
if(Debugging): print Xbins
Ybins = range(ImageHisto.GetYaxis().FindBin(yLo), ImageHisto.GetYaxis().FindBin(yHi))
if(Debugging): print Ybins

# Pull in a list of all the pixel values corresponding to the above bins.
print "\tReading in pixel values from TH2D..."
PixelValues = []
nValues = len(Xbins) * len(Ybins)
iVal = 0
for xbin in Xbins:
  for ybin in Ybins:
    PixelValues.append(ImageHisto.GetBinContent(xbin, ybin))
    iVal += 1
    if((nValues >= 100) and (iVal % int(nValues / 100) == 0)):
      ROOT.StatusBar(iVal, nValues, int(nValues / 100))
print

# Now that we're done with ImageHisto, close the file it came from.
InputFile.Close()

# Build up a histogram of the pixel values
TitleString = "Histogram of Pixel Values in Range: " + str(xLo) + " < x < " + str(xHi) + ", " + str(yLo) + " < y < " + str(yHi)
nBins = 100
PixelValueHisto = ROOT.TH1D("PixelValueHistoZoom", TitleString, nBins, min(PixelValues), max(PixelValues))
PixelValueHisto.GetXaxis().SetTitle("Background Corrected Pixel Values [ADC Units]")
PixelValueHisto.GetXaxis().SetTitleOffset(1.1)
BinWidth = (max(PixelValues) - min(PixelValues)) / float(nBins)
TitleString = "Counts per " + "{:0.1f}".format(BinWidth) + " ADC Unit Bin"
PixelValueHisto.GetYaxis().SetTitle(TitleString)
PixelValueHisto.GetYaxis().SetTitleOffset(1.1)
print "\tWriting pixel values to TH1D..."
iVal = 0
for val in PixelValues:
  PixelValueHisto.Fill(val)
  iVal += 1
  if((nValues >= 100) and (iVal % int(nValues / 100) == 0)):
    ROOT.StatusBar(iVal, nValues, int(nValues / 100))
print

# Get ready and plot this thing.
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.08)
aPad.SetBottomMargin(0.09)
aPad.SetRightMargin(0.02)
aPad.SetLogy(1)
aPad.Draw()
aPad.cd()
PixelValueHisto.Draw()
aCanvas.Update()

# Now save the plot and save the histogram to a root file.
PlotFileName = InputFilePath.replace(".root", "." + OutputTag + ".PixelValues.pdf")
aCanvas.SaveAs(PlotFileName)
OutputFile = ROOT.TFile(PlotFileName.replace(".pdf", ".root"), "RECREATE")
PixelValueHisto.Write()
OutputFile.Close()

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
