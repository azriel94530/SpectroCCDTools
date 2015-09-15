#!/usr/bin/python

####################################################################################################
# Make a plot of the beam spot position on the CCD for different focusing and alignment conditions.#
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

# Lists to store the beam energy and the beam position data:
FocusingStates = ["Pinhole In", "0.25T L", "0.5T L", "0.25T H", "0.5T H", "0.5T H, 0.5T CW", "0.5T H, 0.5T CCW", "0.5T H, 0.25T CCW", "0.5T H, 0T CCW", "1T US", "1T DS"]
FocusingStateN = range(len(FocusingStates))
FocusingStateU = numpy.zeros(len(FocusingStates))
RangeForPlot   = [-0.5, float(FocusingStateN[-1]) + 0.5]
#print FocusingStateN
#print EnergyRangeForPlot
SpotExtentXlo  = [ 4.062,  3.456,  3.046,  4.322,  4.642,  4.622,  4.652,  4.647,  4.637,  4.647,  4.637]
SpotExtentXhi  = [ 4.497,  3.967,  3.596,  4.687,  4.947,  4.937,  4.967,  4.957,  4.952,  4.957,  4.947]
SpotExtentYlo  = [ 5.003,  5.048,  5.138,  5.228,  5.274,  4.597,  6.220,  5.589,  5.319,  5.274,  5.274]
SpotExtentYhi  = [ 7.978,  8.023,  8.023,  7.933,  7.844,  7.392,  8.338,  8.113,  7.888,  7.888,  7.888]
SpotXAvgPos    = [ 4.266,  3.681,  3.287,  4.505,  4.795,  4.777,  4.808,  4.801,  4.792,  4.799,  4.792]
SpotXAvgPosEr  = [ 0.033,  0.041,  0.045,  0.031,  0.020,  0.022,  0.020,  0.021,  0.021,  0.021,  0.021]
SpotMaxXVal    = [ 4.202,  3.651,  3.221,  4.517,  4.782,  4.777,  4.782,  4.792,  4.782,  4.812,  4.772]
SpotMaxYVal    = [ 6.490,  6.490,  6.581,  7.076,  6.536,  5.634,  7.257,  6.761,  6.355,  6.490,  6.455]
SpotAmplitude  = [3894.7, 3914.1, 5481.8, 3476.3, 3632.8, 3655.5, 4326.6, 3786.7, 3566.2, 3862.9, 3702.2]
SpotAmplError  = [ 110.5,  113.5,  132.0,  187.0,  172.4,  154.3,  196.7,  169.7,  174.1,  175.2,  172.6]

# Make the wrap-around lists for the area fill plots:
AFPlot_FocusingStates = []
AFPlot_SpotExtentX = []
AFPlot_SpotExtentY = []
for i in range(len(FocusingStates)):
  AFPlot_FocusingStates.append(FocusingStateN[i])
  AFPlot_SpotExtentX.append(SpotExtentXhi[i])
  AFPlot_SpotExtentY.append(SpotExtentYhi[i])
for i in range(len(FocusingStates)):
  AFPlot_FocusingStates.append(FocusingStateN[-1 * (i + 1)])
  AFPlot_SpotExtentX.append(SpotExtentXlo[-1 * (i + 1)])
  AFPlot_SpotExtentY.append(SpotExtentYlo[-1 * (i + 1)])

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
CanvasSetupHisto = ROOT.TH2D("CanvasSetupHisto", "Plots, plots, plots...", 
                             len(FocusingStates), RangeForPlot[0], RangeForPlot[1], 
                             6000, 0., 6000.)
CanvasSetupHisto.GetXaxis().SetTitle("")
CanvasSetupHisto.GetYaxis().SetTitle("Beam Spot Position [mm]")
CanvasSetupHisto.GetYaxis().SetTitleOffset(0.8)
CanvasSetupHisto.GetYaxis().SetRangeUser(0.95 * min(SpotExtentYlo), 1.05 * max(SpotExtentYhi))
for i in range(len(FocusingStates)):
  CanvasSetupHisto.GetXaxis().SetBinLabel(i + 1, FocusingStates[i])
CanvasSetupHisto.Draw()

# Plot the beam spot y postition as a function of input energy:
#...First, a filled TGraph to show the extent in the y position...
SpotExtentYGraph = ROOT.TGraph(len(AFPlot_FocusingStates), array.array("f", AFPlot_FocusingStates), array.array("f", AFPlot_SpotExtentY))
SpotExtentYGraph.SetTitle("Beam Spot Y Extent")
SpotExtentYGraph.SetFillColorAlpha(ROOT.kRed, 0.67)
SpotExtentYGraph.Draw("samef")
#...Second, a simple line/point graph for the maximum y value...
SpotMaxYGraph = ROOT.TGraph(len(FocusingStates), array.array("f", FocusingStateN), array.array("f", SpotMaxYVal))
SpotMaxYGraph.SetTitle("Max. Y Positon")
SpotMaxYGraph.SetMarkerStyle(20)
SpotMaxYGraph.SetMarkerSize(2)
SpotMaxYGraph.SetMarkerColor(ROOT.kBlack)
SpotMaxYGraph.SetLineWidth(2)
SpotMaxYGraph.SetLineColor(ROOT.kBlack)
SpotMaxYGraph.Draw("samelp")
#...Finally, a TLegend to appropriately annotate the plot...
yPosLegend = ROOT.TLegend(0.795,0.825, 0.975,0.975)
yPosLegend.SetFillColor(ROOT.kWhite)
yPosLegend.SetTextFont(42)
yPosLegend.AddEntry(SpotExtentYGraph, SpotExtentYGraph.GetTitle(), "f")
yPosLegend.AddEntry(SpotMaxYGraph,    SpotMaxYGraph.GetTitle(), "lp")
yPosLegend.Draw()
aCanvas.Update()
aCanvas.SaveAs("./SpotYPos_vs_Focusing.pdf")

# Now let's plot the exposition as a function of wavelength since that's actyally going to be a 
# bit more interesting.
#...Start by rescaling the vertical axis for the *X* positions on the CCD...
CanvasSetupHisto.GetYaxis().SetRangeUser(0.95 * min(SpotExtentXlo), 1.05 * max(SpotExtentXhi))
CanvasSetupHisto.Draw()
#...And a filled extent graph to show the x extent of the plot...
SpotExtentXGraph = ROOT.TGraph(len(AFPlot_FocusingStates), array.array("f", AFPlot_FocusingStates), array.array("f", AFPlot_SpotExtentX))
SpotExtentXGraph.SetTitle("Beam Spot X Extent")
SpotExtentXGraph.SetFillColorAlpha(ROOT.kRed, 0.67)
SpotExtentXGraph.Draw("samef")
#...and a maximum value plot...
SpotMaxXGraph = ROOT.TGraph(len(FocusingStateN), array.array("f", FocusingStateN), array.array("f", SpotMaxXVal))
SpotMaxXGraph.SetTitle("Max. X Positon")
SpotMaxXGraph.SetMarkerStyle(20)
SpotMaxXGraph.SetMarkerSize(2)
SpotMaxXGraph.SetMarkerColor(ROOT.kBlack)
SpotMaxXGraph.SetLineWidth(2)
SpotMaxXGraph.SetLineColor(ROOT.kBlack)
SpotMaxXGraph.Draw("samelp")
#...We're actually more interested in the wieghted average X value plot...
SpotAvgXGraph = ROOT.TGraphErrors(len(FocusingStateN), array.array("f", FocusingStateN), array.array("f", SpotXAvgPos), 
	                                                     array.array("f", FocusingStateU), array.array("f", SpotXAvgPosEr))
SpotAvgXGraph.SetTitle("Avg. X Positon")
SpotAvgXGraph.SetMarkerStyle(21)
SpotAvgXGraph.SetMarkerSize(1)
SpotAvgXGraph.SetMarkerColor(ROOT.kBlue)
SpotAvgXGraph.SetLineWidth(2)
SpotAvgXGraph.SetLineColor(ROOT.kBlue)
SpotAvgXGraph.Draw("samelp")

#...And we'll need a TLegend here too...
xPosLegend = ROOT.TLegend(0.795,0.775, 0.975,0.975)
xPosLegend.SetFillColor(ROOT.kWhite)
xPosLegend.SetTextFont(42)
xPosLegend.AddEntry(SpotExtentXGraph, SpotExtentXGraph.GetTitle(), "f")
xPosLegend.AddEntry(SpotMaxXGraph,    SpotMaxXGraph.GetTitle(),    "lp")
xPosLegend.AddEntry(SpotAvgXGraph,    SpotAvgXGraph.GetTitle(),    "lp")
xPosLegend.Draw()
aCanvas.Update()
aCanvas.SaveAs("./SpotXPos_vs_Focusing.pdf")

#Finally, let's draw the beam spot amplitude under the different bias conditions:
aPad.SetLeftMargin(0.08)
CanvasSetupHisto.GetYaxis().SetRangeUser(0.9 * min(SpotAmplitude), 1.1 * max(SpotAmplitude))
CanvasSetupHisto.GetYaxis().SetTitleOffset(1.1)
CanvasSetupHisto.Draw()
SpotAmplGraph = ROOT.TGraphErrors(len(FocusingStateN), array.array("f", FocusingStateN), array.array("f", SpotAmplitude), 
	                                                     array.array("f", FocusingStateU), array.array("f", SpotAmplError))
SpotAmplGraph.SetTitle("Beam Spot Amplitude")
SpotAmplGraph.GetXaxis().SetTitle(CanvasSetupHisto.GetXaxis().GetTitle())
SpotAmplGraph.GetYaxis().SetRangeUser(0., 900.)
SpotAmplGraph.GetYaxis().SetTitle("Beam Spot Amplitude [ADC Units]")
SpotAmplGraph.SetMarkerStyle(20)
SpotAmplGraph.SetMarkerSize(2)
SpotAmplGraph.SetMarkerColor(ROOT.kBlack)
SpotAmplGraph.SetLineWidth(2)
SpotAmplGraph.SetLineColor(ROOT.kBlack)
SpotAmplGraph.Draw("samelp")
aCanvas.Update()
aCanvas.SaveAs("./SpotAmpl_vs_Focusing.pdf")

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
