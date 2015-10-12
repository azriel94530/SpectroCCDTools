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
States = ["fullBeam_noClipping", "fullBeam_noClipping2", 
          "fullBeam_startClipping", "fullBeam_startClipping2", "fullBeam_startClipping3", "fullBeam_startClipping4", "fullBeam_startClipping5", "fullBeam_startClipping6", "fullBeam_startClipping7",
          "halfBeam_exp500x1000", "halfBeam_exp500x2000", "halfBeam_exp500x5000", "halfBeam_exp500x10000", "halfBeam_exp500x20000", "halfBeam_exp500x50000", "halfBeam_exp500x100000",
          "noBeam_exp500x10000", "noBeam_exp500x50000", "noBeam2_exp500x50000",
          "quarterBeam_exp500x10000", "quarterBeam_exp500x50000", "quarterBeam_exp500x50000_Vsub50V", "quarterBeam_exp500x50000_Vsub80V", "quarterBeam_exp500x50000_Vsub100V"]
StateN = range(len(States))
StateU = numpy.zeros(len(States))
RangeForPlot   = [-0.5, float(StateN[-1]) + 0.5]
#print StateN
#print States
SpotExtentXlo  = [ 4.837,  4.847,  4.832,  4.827,  4.817,  4.827,  4.832,  4.817,  4.812,  4.807,  4.807,  4.807,  4.782,  4.772,  4.742,  4.722,  4.777,  4.767,  4.712,  4.782,  4.742,  4.762,  4.752,  4.747]
SpotExtentXhi  = [ 5.417,  5.437,  5.462,  5.437,  5.447,  5.462,  5.427,  5.447,  5.452,  5.432,  5.437,  5.447,  5.452,  5.462,  5.477,  5.487,  5.372,  5.367,  5.162,  5.427,  5.447,  5.467,  5.472,  5.472]
SpotExtentYlo  = [ 6.671,  6.626,  6.581,  6.581,  6.490,  6.536,  6.581,  6.762,  6.806,  7.888,  7.933,  7.843,  7.798,  7.707,  7.482,  7.392,  9.736,  9.781, 11.539,  8.699,  8.429,  7.798,  7.707,  7.662]
SpotExtentYhi  = [11.133, 11.178, 11.223, 11.268, 11.268, 11.178, 11.133, 11.178, 11.268, 11.494, 11.539, 11.584, 11.629, 11.854, 12.215, 12.485, 12.665, 12.711, 14.108, 11.899, 12.305, 11.989, 12.170, 12.215]
SpotXAvgPos    = [ 5.124,  5.129,  5.144,  5.129,  5.133,  5.136,  5.116,  5.133,  5.127,  5.109,  5.120,  5.115,  5.124,  5.125,  5.123,  5.107,  5.064,  5.061,  4.945,  5.108,  5.098,  5.123,  5.125,  5.122]
SpotXAvgPosEr  = [ 0.064,  0.062,  0.063,  0.061,  0.061,  0.061,  0.061,  0.060,  0.060,  0.060,  0.059,  0.058,  0.065,  0.073,  0.079,  0.089,  0.059,  0.060,  0.045,  0.060,  0.075,  0.074,  0.074,  0.077]
SpotMaxXVal    = [ 5.132,  5.042,  5.197,  5.062,  5.182,  5.142,  5.102,  5.052,  5.092,  5.212,  5.022,  5.142,  5.282,  5.322,  5.342,  5.362,  5.002,  4.972,  4.902,  5.152,  5.322,  5.332,  5.332,  5.342]
SpotMaxYVal    = [ 9.420,  9.105,  8.384,  9.465,  8.969,  8.429, 10.367,  8.789,  9.240, 10.457,  9.781, 10.141,  9.871,  9.555,  9.060,  9.555, 11.088, 11.043, 12.711, 10.457, 10.457,  9.420,  9.060,  9.195]
SpotAmplitude  = [2152.5, 2426.4, 2180.8, 2063.3, 2329.7, 2178.7, 2221.8, 2173.8, 2183.0, 1997.5, 2493.4, 4289.9, 4839.6, 5272.0, 5790.2, 6334.5, 1417.5, 5176.1,  596.8, 5359.7, 5608.4, 8514.1, 6263.3, 5959.3]

# Make the wrap-around lists for the area fill plots:
AFPlot_States = []
AFPlot_SpotExtentX = []
AFPlot_SpotExtentY = []
for i in StateN:
  AFPlot_States.append(StateN[i])
  AFPlot_SpotExtentX.append(SpotExtentXhi[i])
  AFPlot_SpotExtentY.append(SpotExtentYhi[i])
for i in StateN:
  AFPlot_States.append(StateN[-1 * (i + 1)])
  AFPlot_SpotExtentX.append(SpotExtentXlo[-1 * (i + 1)])
  AFPlot_SpotExtentY.append(SpotExtentYlo[-1 * (i + 1)])

# Get ready to plot things!
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.06)
aPad.SetRightMargin(0.19)
aPad.SetBottomMargin(0.15)
aPad.SetTopMargin(0.02)
aPad.SetLogy(0)
aPad.Draw()
aPad.cd()
ROOT.gStyle.SetOptTitle(0)
CanvasSetupHisto = ROOT.TH2D("CanvasSetupHisto", "Plots, plots, plots...", 
                             len(States), RangeForPlot[0], RangeForPlot[1], 
                             10000, 0., 10000.)
CanvasSetupHisto.GetXaxis().SetTitle("")
CanvasSetupHisto.GetYaxis().SetTitle("Beam Spot Position [mm]")
CanvasSetupHisto.GetYaxis().SetTitleOffset(0.8)
CanvasSetupHisto.GetYaxis().SetRangeUser(0.95 * min(SpotExtentYlo), 1.05 * max(SpotExtentYhi))
for i in StateN:
  CanvasSetupHisto.GetXaxis().SetBinLabel(i + 1, States[i])
CanvasSetupHisto.Draw()

# Let's also put in some seperators so that we can see which parts of the plot correspond to which study
SeperatorGraphs = [] 
SeperatorGraphs.append(ROOT.TGraph(2, array.array("f", [ 1.5,  1.5]), array.array("f", [CanvasSetupHisto.GetYaxis().GetXmin(), CanvasSetupHisto.GetYaxis().GetXmax()])))
SeperatorGraphs.append(ROOT.TGraph(2, array.array("f", [ 8.5,  8.5]), array.array("f", [CanvasSetupHisto.GetYaxis().GetXmin(), CanvasSetupHisto.GetYaxis().GetXmax()])))
SeperatorGraphs.append(ROOT.TGraph(2, array.array("f", [15.5, 15.5]), array.array("f", [CanvasSetupHisto.GetYaxis().GetXmin(), CanvasSetupHisto.GetYaxis().GetXmax()])))
SeperatorGraphs.append(ROOT.TGraph(2, array.array("f", [18.5, 18.5]), array.array("f", [CanvasSetupHisto.GetYaxis().GetXmin(), CanvasSetupHisto.GetYaxis().GetXmax()])))
SeperatorGraphs.append(ROOT.TGraph(2, array.array("f", [20.5, 20.5]), array.array("f", [CanvasSetupHisto.GetYaxis().GetXmin(), CanvasSetupHisto.GetYaxis().GetXmax()])))
for seperator in SeperatorGraphs:
  seperator.SetLineColor(ROOT.kBlack)
  seperator.SetLineWidth(3)
  seperator.Draw("samel")

# Plot the beam spot y postition as a function of input energy:
#...First, a filled TGraph to show the extent in the y position...
SpotExtentYGraph = ROOT.TGraph(len(AFPlot_States), array.array("f", AFPlot_States), array.array("f", AFPlot_SpotExtentY))
SpotExtentYGraph.SetTitle("Beam Spot Y Extent")
SpotExtentYGraph.SetFillColorAlpha(ROOT.kRed, 0.67)
SpotExtentYGraph.Draw("samef")
#...Second, a simple line/point graph for the maximum y value...
SpotMaxYGraph = ROOT.TGraph(len(States), array.array("f", StateN), array.array("f", SpotMaxYVal))
SpotMaxYGraph.SetTitle("Max. Y Positon")
SpotMaxYGraph.SetMarkerStyle(20)
SpotMaxYGraph.SetMarkerSize(2)
SpotMaxYGraph.SetMarkerColor(ROOT.kBlack)
SpotMaxYGraph.Draw("samep")
#...Finally, a TLegend to appropriately annotate the plot...
yPosLegend = ROOT.TLegend(0.82,0.825, 0.99,0.975)
yPosLegend.SetFillColor(ROOT.kWhite)
yPosLegend.SetTextFont(42)
yPosLegend.AddEntry(SpotExtentYGraph, SpotExtentYGraph.GetTitle(), "f")
yPosLegend.AddEntry(SpotMaxYGraph,    SpotMaxYGraph.GetTitle(),    "p")
yPosLegend.Draw()
aCanvas.Update()
aCanvas.SaveAs("./SpotYPos.pdf")

# Now let's plot the exposition as a function of wavelength since that's actyally going to be a 
# bit more interesting.
#...Start by rescaling the vertical axis for the *X* positions on the CCD...
CanvasSetupHisto.GetYaxis().SetRangeUser(0.95 * min(SpotExtentXlo), 1.05 * max(SpotExtentXhi))
CanvasSetupHisto.Draw()
# And then redrawing all the seperators.
for seperator in SeperatorGraphs:
  seperator.SetLineColor(ROOT.kBlack)
  seperator.SetLineWidth(3)
  seperator.Draw("samel")
#...And a filled extent graph to show the x extent of the plot...
SpotExtentXGraph = ROOT.TGraph(len(AFPlot_States), array.array("f", AFPlot_States), array.array("f", AFPlot_SpotExtentX))
SpotExtentXGraph.SetTitle("Beam Spot X Extent")
SpotExtentXGraph.SetFillColorAlpha(ROOT.kRed, 0.67)
SpotExtentXGraph.Draw("samef")
#...and a maximum value plot...
SpotMaxXGraph = ROOT.TGraph(len(StateN), array.array("f", StateN), array.array("f", SpotMaxXVal))
SpotMaxXGraph.SetTitle("Max. X Positon")
SpotMaxXGraph.SetMarkerStyle(20)
SpotMaxXGraph.SetMarkerSize(2)
SpotMaxXGraph.SetMarkerColor(ROOT.kBlack)
SpotMaxXGraph.Draw("samep")
#...We're actually more interested in the wieghted average X value plot...
SpotAvgXGraph = ROOT.TGraphErrors(len(StateN), array.array("f", StateN), array.array("f", SpotXAvgPos), 
	                                             array.array("f", StateU), array.array("f", SpotXAvgPosEr))
SpotAvgXGraph.SetTitle("Avg. X Positon")
SpotAvgXGraph.SetMarkerStyle(21)
SpotAvgXGraph.SetMarkerSize(2)
SpotAvgXGraph.SetMarkerColor(ROOT.kBlue)
SpotAvgXGraph.SetLineColor(ROOT.kBlue)
SpotAvgXGraph.Draw("samep")

#...And we'll need a TLegend here too...
xPosLegend = ROOT.TLegend(0.82,0.775, 0.99,0.975)
xPosLegend.SetFillColor(ROOT.kWhite)
xPosLegend.SetTextFont(42)
xPosLegend.AddEntry(SpotExtentXGraph, SpotExtentXGraph.GetTitle(), "f")
xPosLegend.AddEntry(SpotMaxXGraph,    SpotMaxXGraph.GetTitle(),    "p")
xPosLegend.AddEntry(SpotAvgXGraph,    SpotAvgXGraph.GetTitle(),    "p")
xPosLegend.Draw()
aCanvas.Update()
aCanvas.SaveAs("./SpotXPos.pdf")

#Finally, let's draw the beam spot amplitude under the different bias conditions:
aPad.SetLeftMargin(0.08)
CanvasSetupHisto.GetYaxis().SetRangeUser(0., 9000.)
CanvasSetupHisto.GetYaxis().SetTitleOffset(1.1)
CanvasSetupHisto.GetYaxis().SetTitle("Beam Spot Amplitude [ADC Units]")
CanvasSetupHisto.Draw()
# And then redrawing all the seperators.
for seperator in SeperatorGraphs:
  seperator.SetLineColor(ROOT.kBlack)
  seperator.SetLineWidth(3)
  seperator.Draw("samel")
SpotAmplGraph = ROOT.TGraph(len(StateN), array.array("f", StateN), array.array("f", SpotAmplitude))
SpotAmplGraph.SetTitle("Beam Spot Amplitude")
SpotAmplGraph.GetXaxis().SetTitle(CanvasSetupHisto.GetXaxis().GetTitle())
#SpotAmplGraph.GetYaxis().SetRangeUser(0., 900.)
SpotAmplGraph.GetYaxis().SetTitle("Beam Spot Amplitude [ADC Units]")
SpotAmplGraph.SetMarkerStyle(20)
SpotAmplGraph.SetMarkerSize(2)
SpotAmplGraph.SetMarkerColor(ROOT.kBlack)
SpotAmplGraph.Draw("samep")
aCanvas.Update()
aCanvas.SaveAs("./SpotAmpl.pdf")

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
