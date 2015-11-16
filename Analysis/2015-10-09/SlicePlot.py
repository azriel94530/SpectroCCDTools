#!/usr/bin/python

####################################################################################################
# Plot the 
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

# Go get the root file with the image histogram in it, then pull out the image histogram.
ImageHistoFile = ROOT.TFile("../../../Images/2015-10-09/quarterBeam_exp500x50000/quarterBeam_exp500x50000_UnShuf.root")
ImageHisto = ImageHistoFile.Get("thatHistogram")
ImageHisto.SetName("ImageHisto")

# Now zoom in on the beam spot and get the x and y bins to loop over
xLo =  4.7
xHi =  5.5
yLo =  8.5
yHi = 12.5
ImageHisto.GetXaxis().SetRangeUser(xLo, xHi)
ImageHisto.GetYaxis().SetRangeUser(yLo, yHi)
Xbins = range(ImageHisto.GetXaxis().FindBin(xLo), ImageHisto.GetXaxis().FindBin(xHi))
if(Debugging): print Xbins
Ybins = range(ImageHisto.GetYaxis().FindBin(yLo), ImageHisto.GetYaxis().FindBin(yHi))
if(Debugging): print Ybins

# Make a few TH1D objects to hold the Sum(N) spectra.
PixValLo = 0.
PixValHi = 6000.
nPixValBins = 600
PixValHisto_Sum1 = PythonTools.MakePixValHisto("PixValHisto_Sum1", "Sum(1) Histogram", nPixValBins, PixValLo, PixValHi, ROOT.kBlack)

# Now loop over the bins in the beam spot window and populate the Sum(N) spectra
for xbin in Xbins:
  for ybin in Ybins:
    Sum1Val = ImageHisto.GetBinContent(xbin, ybin)
    PixValHisto_Sum1.Fill(Sum1Val)

# Get ready to plot things!
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.08)
aPad.SetRightMargin(0.025)
aPad.SetBottomMargin(0.08)
aPad.SetTopMargin(0.02)
aPad.SetLogy(1)
aPad.Draw()
aPad.cd()
ROOT.gStyle.SetOptTitle(0)

# Plot the spectrum:
PixValHisto_Sum1.Draw()

# Pull up a two-Gaussian fit model and fit it to the spectrum...
FitModel = PythonTools.GetTwoGausFitModel("FitModel", PixValHisto_Sum1, 3700., 350., 4700., 400.)
PixValHisto_Sum1.Fit(FitModel, "LLEM", "", 3100., 6000.)

# Now report the difference between the high and low Gaussians:
print "\tTwo Gaussian means at:", "{:3.1f}".format(FitModel.GetParameter(2)), "+/-", "{:3.1f}".format(FitModel.GetParError(2)), "and", "{:3.1f}".format(FitModel.GetParameter(5)), "+/-", "{:3.1f}".format(FitModel.GetParError(5))
print "\t  for a difference of:", "{:3.1f}".format(FitModel.GetParameter(5) - FitModel.GetParameter(2)), "+/-", "{:3.1f}".format(numpy.sqrt((FitModel.GetParError(2)**2.) + (FitModel.GetParError(5)**2.)))

# Save the plot...
aCanvas.Update()
aCanvas.SaveAs(PixValHisto_Sum1.GetName() + ".pdf")

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
