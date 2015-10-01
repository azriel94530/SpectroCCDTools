#!/usr/bin/python

####################################################################################################
# Make a of the width and mean of the noise levels for a bunch of dark images from 2015-09-23.     #
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

# Lists to store descriptions of the dark images and supporting information for each plot.
DarkImageDescr = ["Lights on, Cover off", "Lights on, Cover on", "Lights off, Cover on", "Lights off, Cover off"]
NDarkImages = 5
DarkImageN = range(NDarkImages)
RangeForPlot = [-0.5, float(DarkImageN[-1]) + 0.5]
xForPlot = array.array("f", range(NDarkImages))
Zeros = array.array("f", [0., 0., 0., 0., 0.])

# Noise peak fit results.
LightsOnMeanVal = [-3.197, -3.225, -3.201, -3.262, -3.724]
LightsOnMeanUnc = [ 0.038,  0.038,  0.038,  0.038,  0.038]
LightsOnSigmVal = [45.089, 44.918, 44.820, 44.824, 44.871]
LightsOnSigmUnc = [ 0.040,  0.039,  0.039,  0.039,  0.040]
CoverOnMeanVal = [-1.272, -1.223, -1.580, -1.502, -1.310]
CoverOnMeanUnc = [ 0.035,  0.035,  0.035,  0.035,  0.035]
CoverOnSigmVal = [42.092, 41.769, 41.802, 41.920, 41.876]
CoverOnSigmUnc = [ 0.033,  0.032,  0.032,  0.032,  0.032]
LightsOffCoverOnMeanVal = [-1.147, -0.999, -1.137, -1.285, -0.857]
LightsOffCoverOnMeanUnc = [ 0.035,  0.035,  0.035,  0.035,  0.035]
LightsOffCoverOnSigmVal = [41.954, 41.855, 41.878, 41.610, 41.811]
LightsOffCoverOnSigmUnc = [ 0.032,  0.032,  0.032,  0.032,  0.032]
LightsOffCoverOffMeanVal = [-2.576, -2.588, -2.154, -1.907, -2.424]
LightsOffCoverOffMeanUnc = [ 0.036,  0.036,  0.036,  0.035,  0.036]
LightsOffCoverOffSigmVal = [42.933, 42.696, 42.770, 42.270, 42.836]
LightsOffCoverOffSigmUnc = [ 0.034,  0.034,  0.034,  0.033,  0.034]

# Make some TGraph objects for these data.
MarkerSize = 3
# First the means...
LightsOnMeanGraph = ROOT.TGraphErrors(NDarkImages, xForPlot, array.array("f", LightsOnMeanVal), Zeros, array.array("f", LightsOnMeanUnc))
LightsOnMeanGraph.SetMarkerStyle(20)
LightsOnMeanGraph.SetMarkerSize(MarkerSize)
LightsOnMeanGraph.SetMarkerColor(ROOT.kBlack)
LightsOnMeanGraph.SetLineColor(ROOT.kBlack)
CoverOnMeanGraph = ROOT.TGraphErrors(NDarkImages, xForPlot, array.array("f", CoverOnMeanVal), Zeros, array.array("f", CoverOnMeanUnc))
CoverOnMeanGraph.SetMarkerStyle(21)
CoverOnMeanGraph.SetMarkerSize(MarkerSize)
CoverOnMeanGraph.SetMarkerColor(ROOT.kBlue)
CoverOnMeanGraph.SetLineColor(ROOT.kBlue)
LightsOffCoverOnMeanGraph = ROOT.TGraphErrors(NDarkImages, xForPlot, array.array("f", LightsOffCoverOnMeanVal), Zeros, array.array("f", LightsOffCoverOnMeanUnc))
LightsOffCoverOnMeanGraph.SetMarkerStyle(22)
LightsOffCoverOnMeanGraph.SetMarkerSize(MarkerSize)
LightsOffCoverOnMeanGraph.SetMarkerColor(ROOT.kGreen - 1)
LightsOffCoverOnMeanGraph.SetLineColor(ROOT.kGreen - 1)
LightsOffCoverOffMeanGraph = ROOT.TGraphErrors(NDarkImages, xForPlot, array.array("f", LightsOffCoverOffMeanVal), Zeros, array.array("f", LightsOffCoverOffMeanUnc))
LightsOffCoverOffMeanGraph.SetMarkerStyle(23)
LightsOffCoverOffMeanGraph.SetMarkerSize(MarkerSize)
LightsOffCoverOffMeanGraph.SetMarkerColor(ROOT.kRed)
LightsOffCoverOffMeanGraph.SetLineColor(ROOT.kRed)
# Now the sigmas...
LightsOnSigmGraph = ROOT.TGraphErrors(NDarkImages, xForPlot, array.array("f", LightsOnSigmVal), Zeros, array.array("f", LightsOnSigmUnc))
LightsOnSigmGraph.SetMarkerStyle(20)
LightsOnSigmGraph.SetMarkerSize(MarkerSize)
LightsOnSigmGraph.SetMarkerColor(ROOT.kBlack)
LightsOnSigmGraph.SetLineColor(ROOT.kBlack)
CoverOnSigmGraph = ROOT.TGraphErrors(NDarkImages, xForPlot, array.array("f", CoverOnSigmVal), Zeros, array.array("f", CoverOnSigmUnc))
CoverOnSigmGraph.SetMarkerStyle(21)
CoverOnSigmGraph.SetMarkerSize(MarkerSize)
CoverOnSigmGraph.SetMarkerColor(ROOT.kBlue)
CoverOnSigmGraph.SetLineColor(ROOT.kBlue)
LightsOffCoverOnSigmGraph = ROOT.TGraphErrors(NDarkImages, xForPlot, array.array("f", LightsOffCoverOnSigmVal), Zeros, array.array("f", LightsOffCoverOnSigmUnc))
LightsOffCoverOnSigmGraph.SetMarkerStyle(22)
LightsOffCoverOnSigmGraph.SetMarkerSize(MarkerSize)
LightsOffCoverOnSigmGraph.SetMarkerColor(ROOT.kGreen - 1)
LightsOffCoverOnSigmGraph.SetLineColor(ROOT.kGreen - 1)
LightsOffCoverOffSigmGraph = ROOT.TGraphErrors(NDarkImages, xForPlot, array.array("f", LightsOffCoverOffSigmVal), Zeros, array.array("f", LightsOffCoverOffSigmUnc))
LightsOffCoverOffSigmGraph.SetMarkerStyle(23)
LightsOffCoverOffSigmGraph.SetMarkerSize(MarkerSize)
LightsOffCoverOffSigmGraph.SetMarkerColor(ROOT.kRed)
LightsOffCoverOffSigmGraph.SetLineColor(ROOT.kRed)

# Get ready to plot things!
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.06)
aPad.SetRightMargin(0.02)
aPad.SetBottomMargin(0.09)
aPad.SetTopMargin(0.02)
aPad.SetLogy(0)
aPad.Draw()
aPad.cd()
ROOT.gStyle.SetOptTitle(0)

# First, lets do the noise means.
yMin = 1.e6
yMax = -1.e6
for thisList in [LightsOnMeanVal, CoverOnMeanVal, LightsOffCoverOnMeanVal, LightsOffCoverOffMeanVal]:
  for value in thisList:
    if(value < yMin): yMin = value
    if(value > yMax): yMax = value
CanvasSetupHisto = ROOT.TH2D("CanvasSetupHisto", "Plots, plots, plots...", 
                             1, RangeForPlot[0], RangeForPlot[1], 1, yMin - (0.1 * numpy.abs(yMin)) , yMax + (0.1 * numpy.abs(yMax)))
CanvasSetupHisto.GetXaxis().SetTitle("Dark Image Number")
CanvasSetupHisto.GetYaxis().SetTitle("Noise Peak Mean [ADC Units]")
CanvasSetupHisto.GetYaxis().SetTitleOffset(0.8)
CanvasSetupHisto.Draw()
LightsOnMeanGraph.Draw("samep")
CoverOnMeanGraph.Draw("samep")
LightsOffCoverOnMeanGraph.Draw("samep")
LightsOffCoverOffMeanGraph.Draw("samep")
MeanGraphLegend = ROOT.TLegend(0.09,0.115, 0.45,0.30)
MeanGraphLegend.SetFillColor(ROOT.kWhite)
MeanGraphLegend.SetTextFont(42)
MeanGraphLegend.SetNColumns(2)
MeanGraphLegend.AddEntry(LightsOnMeanGraph,          DarkImageDescr[0], "p")
MeanGraphLegend.AddEntry(CoverOnMeanGraph,           DarkImageDescr[1], "p")
MeanGraphLegend.AddEntry(LightsOffCoverOnMeanGraph,  DarkImageDescr[2], "p")
MeanGraphLegend.AddEntry(LightsOffCoverOffMeanGraph, DarkImageDescr[3], "p")
MeanGraphLegend.Draw()
aCanvas.Update()
aCanvas.SaveAs("./NoiseMeanGraphs.pdf")
del CanvasSetupHisto

# Now, lets do the noise sigmas.
yMin = 1.e6
yMax = -1.e6
for thisList in [LightsOnSigmVal, CoverOnSigmVal, LightsOffCoverOnSigmVal, LightsOffCoverOffSigmVal]:
  for value in thisList:
    if(value < yMin): yMin = value
    if(value > yMax): yMax = value
CanvasSetupHisto = ROOT.TH2D("CanvasSetupHisto", "Plots, plots, plots...", 
                             1, RangeForPlot[0], RangeForPlot[1], 1, yMin - (0.1 * numpy.abs(yMin)) , yMax + (0.05 * numpy.abs(yMax)))
CanvasSetupHisto.GetXaxis().SetTitle("Dark Image Number")
CanvasSetupHisto.GetYaxis().SetTitle("Noise Peak Sigma [ADC Units]")
CanvasSetupHisto.GetYaxis().SetTitleOffset(0.8)
CanvasSetupHisto.Draw()
LightsOnSigmGraph.Draw("samep")
CoverOnSigmGraph.Draw("samep")
LightsOffCoverOnSigmGraph.Draw("samep")
LightsOffCoverOffSigmGraph.Draw("samep")
SigmGraphLegend = ROOT.TLegend(0.09,0.115, 0.45,0.30)
SigmGraphLegend.SetFillColor(ROOT.kWhite)
SigmGraphLegend.SetTextFont(42)
SigmGraphLegend.SetNColumns(2)
SigmGraphLegend.AddEntry(LightsOnSigmGraph,          DarkImageDescr[0], "p")
SigmGraphLegend.AddEntry(CoverOnSigmGraph,           DarkImageDescr[1], "p")
SigmGraphLegend.AddEntry(LightsOffCoverOnSigmGraph,  DarkImageDescr[2], "p")
SigmGraphLegend.AddEntry(LightsOffCoverOffSigmGraph, DarkImageDescr[3], "p")
SigmGraphLegend.Draw()
aCanvas.Update()
aCanvas.SaveAs("./NoiseSigmGraphs.pdf")

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
