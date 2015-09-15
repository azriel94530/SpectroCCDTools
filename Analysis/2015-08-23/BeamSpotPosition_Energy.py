#!/usr/bin/python

####################################################################################################
# Make a plot of the beam spot position on CCD for energies near 1 keV.                            #
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
EnergyRangeForPlot = [0.825, 1.075]
BeamEnergy    = [0.875, 0.900, 0.950, 1.000, 1.050]
BeamEnergyUnc = [0.,    0.,    0.,    0.,    0.   ]# We'll just assume the beam energy is perfectly known for now...
SpotExtentXlo = [9.374, 8.193, 5.937, 3.897, 2.001]
SpotExtentXhi = [9.584, 8.403, 6.157, 4.107, 2.216]
SpotExtentYlo = [5.859, 6.040, 5.724, 5.724, 5.724]
SpotExtentYhi = [6.941, 7.076, 7.392, 7.482, 7.302]
SpotXAvgPos   = [9.479, 8.295, 6.049, 4.004, 2.108]
SpotXAvgPosEr = [0.029, 0.029, 0.028, 0.027, 0.029]
SpotMaxXVal   = [9.479, 8.293, 6.042, 4.002, 2.111]
SpotMaxYVal   = [6.400, 6.536, 6.581, 6.536, 6.536]

# Make the wrap-around lists for the area fill plots:
AFPlot_BeamEnergy = []
AFPlot_SpotExtentX = []
AFPlot_SpotExtentY = []
for i in range(len(BeamEnergy)):
  AFPlot_BeamEnergy.append(BeamEnergy[i])
  AFPlot_SpotExtentX.append(SpotExtentXhi[i])
  AFPlot_SpotExtentY.append(SpotExtentYhi[i])
for i in range(len(BeamEnergy)):
  AFPlot_BeamEnergy.append(BeamEnergy[-1 * (i + 1)])
  AFPlot_SpotExtentX.append(SpotExtentXlo[-1 * (i + 1)])
  AFPlot_SpotExtentY.append(SpotExtentYlo[-1 * (i + 1)])
#print AFPlot_BeamEnergy
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
                             1, EnergyRangeForPlot[0], EnergyRangeForPlot[1], 
                             300, 0., 30.)
CanvasSetupHisto.GetXaxis().SetTitle("Incident Photon Energy [keV]")
CanvasSetupHisto.GetYaxis().SetTitle("Beam Spot Position [mm]")
CanvasSetupHisto.GetYaxis().SetTitleOffset(0.8)
CanvasSetupHisto.GetYaxis().SetRangeUser(0.9 * min(SpotExtentYlo), 1.1 * max(SpotExtentYhi))
CanvasSetupHisto.Draw()

# OK, as a warmup, plot the beam spot y postition as a function of input energy:
#...First, a filled TGraph to show the extent in the y position...
SpotExtentYGraph = ROOT.TGraph(len(AFPlot_BeamEnergy), array.array("f", AFPlot_BeamEnergy), array.array("f", AFPlot_SpotExtentY))
SpotExtentYGraph.SetTitle("Beam Spot Y Extent")
SpotExtentYGraph.SetFillColorAlpha(ROOT.kRed, 0.67)
SpotExtentYGraph.Draw("samef")
#...Second, a simple line/point graph for the maximum y value...
SpotMaxYGraph = ROOT.TGraph(len(BeamEnergy), array.array("f", BeamEnergy), array.array("f", SpotMaxYVal))
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
aCanvas.SaveAs("./SpotYPos_vs_Energy.pdf")

# Now let's plot the exposition as a function of wavelength since that's actyally going to be a 
# bit more interesting.
#...Start by rescaling the vertical axis for the *X* positions on the CCD...
CanvasSetupHisto.GetYaxis().SetRangeUser(0.9 * min(SpotExtentXlo), 1.3 * max(SpotExtentXhi))
CanvasSetupHisto.Draw()
#...And a filled extent graph to show the x extent of the plot...
SpotExtentXGraph = ROOT.TGraph(len(AFPlot_BeamEnergy), array.array("f", AFPlot_BeamEnergy), array.array("f", AFPlot_SpotExtentX))
SpotExtentXGraph.SetTitle("Beam Spot X Extent")
SpotExtentXGraph.SetFillColorAlpha(ROOT.kRed, 0.67)
SpotExtentXGraph.Draw("samef")
#...and a maximum value plot...
SpotMaxXGraph = ROOT.TGraph(len(BeamEnergy), array.array("f", BeamEnergy), array.array("f", SpotMaxXVal))
SpotMaxXGraph.SetTitle("Max. X Positon")
SpotMaxXGraph.SetMarkerStyle(20)
SpotMaxXGraph.SetMarkerSize(2)
SpotMaxXGraph.SetMarkerColor(ROOT.kBlack)
SpotMaxXGraph.SetLineWidth(2)
SpotMaxXGraph.SetLineColor(ROOT.kBlack)
SpotMaxXGraph.Draw("samelp")
#...We're actually more interested in the wieghted average X value plot...
SpotAvgXGraph = ROOT.TGraphErrors(len(BeamEnergy), array.array("f", BeamEnergy), array.array("f", SpotXAvgPos), array.array("f", BeamEnergyUnc), array.array("f", SpotXAvgPosEr))
SpotAvgXGraph.SetTitle("Avg. X Positon")
SpotAvgXGraph.SetMarkerStyle(21)
SpotAvgXGraph.SetMarkerSize(1)
SpotAvgXGraph.SetMarkerColor(ROOT.kBlue)
SpotAvgXGraph.SetLineWidth(2)
SpotAvgXGraph.SetLineColor(ROOT.kBlue)
SpotAvgXGraph.Draw("samelp")
#...Let's also do a fit to the spot average...
SpotAvgXFit = ROOT.TF1("SpotAvgXFit", "[0] + ([1] * x) + ([2] * (x^2))", EnergyRangeForPlot[0], EnergyRangeForPlot[1])
SpotAvgXFit.SetParName(  0, "Const.")
SpotAvgXFit.SetParameter(0, 45.)
SpotAvgXFit.SetParName(  1, "Linear")
SpotAvgXFit.SetParameter(1, (max(SpotXAvgPos) - min(SpotXAvgPos)) / (EnergyRangeForPlot[1] - EnergyRangeForPlot[0]))
SpotAvgXFit.SetParName(  2, "Quadr.")
SpotAvgXFit.SetParameter(2, 0.)
SpotAvgXGraph.Fit("SpotAvgXFit", "NEM", "", float(min(BeamEnergy)), float(max(BeamEnergy)))
#...Create a version of the fit we can use to extrapolate down to the beam energies we couldn't
# see in the initial test...
SpotAvgXFit_Disp = ROOT.TF1("SpotAvgXFit", "[0] + ([1] * x) + ([2] * (x^2))", EnergyRangeForPlot[0], EnergyRangeForPlot[1])
SpotAvgXFit_Disp.FixParameter(0, SpotAvgXFit.GetParameter(0))
SpotAvgXFit_Disp.FixParameter(1, SpotAvgXFit.GetParameter(1))
SpotAvgXFit_Disp.FixParameter(2, SpotAvgXFit.GetParameter(2))
SpotAvgXFit_Disp.SetLineColor(ROOT.kGreen - 1)
SpotAvgXFit_Disp.Draw("samel")
#...We should also include an annotation for this plot that shows some salient fit results...
Chi2 = SpotAvgXFit.GetChisquare()
NDF = SpotAvgXFit.GetNDF()
PVal = SpotAvgXFit.GetProb()
FitText = ROOT.TPaveText(0.08,0.12,0.28,0.32,"blNDC")
FitText.SetName("FieldText")
FitText.SetBorderSize(1)
FitText.SetFillColor(ROOT.kWhite)
FitText.SetTextFont(42)
FitText.AddText("#chi^{2} per Deg. of Freedom:")
FitText.AddText("{:2.2f}".format(Chi2) + " / " + str(NDF) + " = " "{:1.3f}".format(Chi2 / float(NDF)))
FitText.AddText("P-Value = " + "{:1.7f}".format(PVal))
FitText.AddText("Lin. Coef. = " + "{:3.2f}".format(SpotAvgXFit.GetParameter(1)) + " #pm " + "{:3.2f}".format(SpotAvgXFit.GetParError(1)))
FitText.AddText("Qu. Coef. = " + "{:3.2f}".format(SpotAvgXFit.GetParameter(2)) + " #pm " + "{:3.2f}".format(SpotAvgXFit.GetParError(2)))
FitText.Draw()

#...And we'll need a TLegend here too...
xPosLegend = ROOT.TLegend(0.795,0.725, 0.975,0.975)
xPosLegend.SetFillColor(ROOT.kWhite)
xPosLegend.SetTextFont(42)
xPosLegend.AddEntry(SpotExtentXGraph, SpotExtentXGraph.GetTitle(), "f")
xPosLegend.AddEntry(SpotMaxXGraph,    SpotMaxXGraph.GetTitle(),    "lp")
xPosLegend.AddEntry(SpotAvgXGraph,    SpotAvgXGraph.GetTitle(),    "lp")
xPosLegend.AddEntry(SpotAvgXFit_Disp, "Fit to Avg. X",             "l")
xPosLegend.Draw()
aCanvas.Update()
aCanvas.SaveAs("./SpotXPos_vs_Energy.pdf")

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
