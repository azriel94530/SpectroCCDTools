#!/usr/bin/python

####################################################################################################
# Make a plot of the beam spot position on the CCD and its amplitude for different substrate       #
# voltages.
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
BiasRangeForPlot = [45, 105.]
BiasVoltage    = [50.,   60.,   80.,   100.]
BiasVoltageUnc = [0.,    0.,    0.,    0.]
SpotExtentXlo  = [8.188, 8.208, 8.193, 8.188]
SpotExtentXhi  = [8.398, 8.418, 8.403, 8.398]
SpotExtentYlo  = [5.950, 6.716, 6.040, 5.769]
SpotExtentYhi  = [7.076, 7.753, 7.076, 7.122]
SpotXAvgPos    = [8.290, 8.312, 8.295, 8.292]
SpotXAvgPosEr  = [0.029, 0.029, 0.029, 0.029]
SpotMaxXVal    = [8.293, 8.313, 8.298, 8.293]
SpotMaxYVal    = [6.536, 7.212, 6.536, 6.445]
SpotAmplitude  = [486.7, 534.5, 736.2, 494.4]
SpotAmplError  = [ 90.9,  91.8,  90.1, 102.8]

# Make the wrap-around lists for the area fill plots:
AFPlot_BiasVoltage = []
AFPlot_SpotExtentX = []
AFPlot_SpotExtentY = []
for i in range(len(BiasVoltage)):
  AFPlot_BiasVoltage.append(BiasVoltage[i])
  AFPlot_SpotExtentX.append(SpotExtentXhi[i])
  AFPlot_SpotExtentY.append(SpotExtentYhi[i])
for i in range(len(BiasVoltage)):
  AFPlot_BiasVoltage.append(BiasVoltage[-1 * (i + 1)])
  AFPlot_SpotExtentX.append(SpotExtentXlo[-1 * (i + 1)])
  AFPlot_SpotExtentY.append(SpotExtentYlo[-1 * (i + 1)])
#print AFPlot_BiasVoltage
#print AFPlot_SpotExtentX
#print AFPlot_SpotExtentY

# Get ready to plot things!
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.06)
aPad.SetRightMargin(0.02)
aPad.SetBottomMargin(0.08)
aPad.SetTopMargin(0.02)
aPad.SetLogy(0)
aPad.Draw()
aPad.cd()
ROOT.gStyle.SetOptTitle(0)
CanvasSetupHisto = ROOT.TH2D("CanvasSetupHisto", "Plots, plots, plots...", 
                             1, BiasRangeForPlot[0], BiasRangeForPlot[1], 
                             300, 0., 30.)
CanvasSetupHisto.GetXaxis().SetTitle("Substrate Bias Voltage [V]")
CanvasSetupHisto.GetYaxis().SetTitle("Beam Spot Position [mm]")
CanvasSetupHisto.GetYaxis().SetTitleOffset(0.8)
CanvasSetupHisto.GetYaxis().SetRangeUser(0.95 * min(SpotExtentYlo), 1.05 * max(SpotExtentYhi))
CanvasSetupHisto.Draw()

# OK, as a warmup, plot the beam spot y postition as a function of input energy:
#...First, a filled TGraph to show the extent in the y position...
SpotExtentYGraph = ROOT.TGraph(len(AFPlot_BiasVoltage), array.array("f", AFPlot_BiasVoltage), array.array("f", AFPlot_SpotExtentY))
SpotExtentYGraph.SetTitle("Beam Spot Y Extent")
SpotExtentYGraph.SetFillColorAlpha(ROOT.kRed, 0.67)
SpotExtentYGraph.Draw("samef")
#...Second, a simple line/point graph for the maximum y value...
SpotMaxYGraph = ROOT.TGraph(len(BiasVoltage), array.array("f", BiasVoltage), array.array("f", SpotMaxYVal))
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
aCanvas.SaveAs("./SpotYPos_vs_Bais.pdf")

# Now let's plot the exposition as a function of wavelength since that's actyally going to be a 
# bit more interesting.
#...Start by rescaling the vertical axis for the *X* positions on the CCD...
CanvasSetupHisto.GetYaxis().SetRangeUser(0.95 * min(SpotExtentXlo), 1.05 * max(SpotExtentXhi))
CanvasSetupHisto.Draw()
#...And a filled extent graph to show the x extent of the plot...
SpotExtentXGraph = ROOT.TGraph(len(AFPlot_BiasVoltage), array.array("f", AFPlot_BiasVoltage), array.array("f", AFPlot_SpotExtentX))
SpotExtentXGraph.SetTitle("Beam Spot X Extent")
SpotExtentXGraph.SetFillColorAlpha(ROOT.kRed, 0.67)
SpotExtentXGraph.Draw("samef")
#...and a maximum value plot...
SpotMaxXGraph = ROOT.TGraph(len(BiasVoltage), array.array("f", BiasVoltage), array.array("f", SpotMaxXVal))
SpotMaxXGraph.SetTitle("Max. X Positon")
SpotMaxXGraph.SetMarkerStyle(20)
SpotMaxXGraph.SetMarkerSize(2)
SpotMaxXGraph.SetMarkerColor(ROOT.kBlack)
SpotMaxXGraph.SetLineWidth(2)
SpotMaxXGraph.SetLineColor(ROOT.kBlack)
SpotMaxXGraph.Draw("samelp")
#...We're actually more interested in the wieghted average X value plot...
SpotAvgXGraph = ROOT.TGraphErrors(len(BiasVoltage), array.array("f", BiasVoltage),   array.array("f", SpotXAvgPos), 
	                                               array.array("f", BiasVoltageUnc), array.array("f", SpotXAvgPosEr))
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
aCanvas.SaveAs("./SpotXPos_vs_Bias.pdf")

#Finally, let's draw the beam spot amplitude under the different bias conditions:
aPad.SetLeftMargin(0.07)
SpotAmplGraph = ROOT.TGraphErrors(len(BiasVoltage), array.array("f", BiasVoltage),    array.array("f", SpotAmplitude), 
	                                                array.array("f", BiasVoltageUnc), array.array("f", SpotAmplError))
SpotAmplGraph.SetTitle("Beam Spot Amplitude")
SpotAmplGraph.GetXaxis().SetTitle(CanvasSetupHisto.GetXaxis().GetTitle())
SpotAmplGraph.GetYaxis().SetRangeUser(0., 900.)
SpotAmplGraph.GetYaxis().SetTitle("Beam Spot Amplitude [ADC Units]")
SpotAmplGraph.SetMarkerStyle(20)
SpotAmplGraph.SetMarkerSize(2)
SpotAmplGraph.SetMarkerColor(ROOT.kBlack)
SpotAmplGraph.SetLineWidth(2)
SpotAmplGraph.SetLineColor(ROOT.kBlack)
SpotAmplGraph.Draw("alp")
aCanvas.Update()
aCanvas.SaveAs("./SpotAmpl_vs_Bias.pdf")

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
