#!/usr/bin/python

####################################################################################################
# Make a plot of the the energy scale, resolution, and amplitude for the different x ray exposrues #
# we took on August 3, 2015.                                                                       #
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
RangeForPlot = [0.5, 9.5]
SumNumber    = [1.,       3.,      5.,      7.,      9.]
SumNumberUnc = [0.,       0.,      0.,      0.,      0.]
# noClearXray1:
Norm1        = [ 19.17,  14.02,    8.19,    7.41,    7.08]
Norm1Unc     = [  0.81,   1.76,    0.80,    0.86,    0.71]
Mean1        = [664.96, 916.83, 1661.13, 1908.08, 1978.30]
Mean1Unc     = [ 13.23,  29.89,   31.80,   38.73,   34.58]
Sigma1       = [211.29, 266.65,  254.12,  278.47,  286.54]
Sigma1Unc    = [ 11.52,  15.58,   17.96,   20.47,   21.59]
# noClearXray2:
Norm2        = [19.61,     7.53,    9.03,    7.91,    7.30]
Norm2Unc     = [ 0.78,     1.72,    0.74,    0.63,    0.82]
Mean2        = [617.57, 1044.01, 1619.79, 1889.33, 1960.68]
Mean2Unc     = [ 20.61,   43.44,   28.16,   25.06,   39.10]
Sigma2       = [242.70,  204.34,  274.44,  264.76,  294.54]
Sigma2Unc    = [ 15.22,   19.66,   16.93,   15.61,   21.46]
# noClearXray3:
Norm3        = [ 19.20,    9.07,    6.69,    7.09,    4.94]
Norm3Unc     = [  0.81,    1.80,    0.79,    0.68,    0.80]
Mean3        = [673.13, 1000.27, 1722.69, 1913.62, 2068.02]
Mean3Unc     = [ 16.26,   44.77,   35.90,   30.70,   39.10]
Sigma3       = [212.32,  232.59,  236.63,  257.52,  248.23]
Sigma3Unc    = [ 12.08,   21.22,   20.61,   17.81,   22.42]
# noClearXray4:
Norm4        = [ 19.70,    6.13,    7.57,    7.76,    5.42]
Norm4Unc     = [  0.84,    1.32,    0.82,    0.77,    0.56]
Mean4        = [631.39, 1048.20, 1642.82, 1835.78, 2012.73]
Mean4Unc     = [ 22.25,   41.14,   35.90,   36.70,   38.76]
Sigma4       = [225.60,  208.00,  267.07,  305.30,  270.73]
Sigma4Unc    = [ 15.40,   22.69,   22.17,   25.67,   26.15]

# Get ready to plot things!
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.07)
aPad.SetRightMargin(0.02)
aPad.SetBottomMargin(0.08)
aPad.SetTopMargin(0.02)
aPad.SetLogy(0)
aPad.Draw()
aPad.cd()
ROOT.gStyle.SetOptTitle(0)
# Let's start by just plotting the above quanties as a function of pixel sum number...
#...First, let's do the canvas setup...
CanvasSetupHisto = ROOT.TH2D("CanvasSetupHisto", "Plots, plots, plots...", 
                             1, RangeForPlot[0], RangeForPlot[1], 
                             2500, 0., 2500.)
CanvasSetupHisto.GetXaxis().SetTitle("Pixel Sum Number")
CanvasSetupHisto.GetYaxis().SetTitle("^{55}Fe Peak Amplitude [Counts per Bin]")
CanvasSetupHisto.GetYaxis().SetTitleOffset(1.0)
CanvasSetupHisto.GetYaxis().SetRangeUser(0., 20.)
CanvasSetupHisto.Draw()
#...Now the peak normalization graphs...
Norm1Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", Norm1), 
                                               array.array("f", SumNumberUnc), array.array("f", Norm1Unc))
Norm1Graph.SetMarkerStyle(20)
Norm1Graph.SetMarkerSize(2)
Norm1Graph.SetMarkerColor(ROOT.kBlack)
Norm1Graph.SetLineWidth(2)
Norm1Graph.SetLineColor(ROOT.kBlack)
Norm1Graph.Draw("samelp")
Norm2Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", Norm2), 
                                               array.array("f", SumNumberUnc), array.array("f", Norm2Unc))
Norm2Graph.SetMarkerStyle(21)
Norm2Graph.SetMarkerSize(2)
Norm2Graph.SetMarkerColor(ROOT.kBlue)
Norm2Graph.SetLineWidth(2)
Norm2Graph.SetLineColor(ROOT.kBlue)
Norm2Graph.Draw("samelp")
Norm3Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", Norm3), 
                                               array.array("f", SumNumberUnc), array.array("f", Norm3Unc))
Norm3Graph.SetMarkerStyle(22)
Norm3Graph.SetMarkerSize(2)
Norm3Graph.SetMarkerColor(ROOT.kGreen - 1)
Norm3Graph.SetLineWidth(2)
Norm3Graph.SetLineColor(ROOT.kGreen - 1)
Norm3Graph.Draw("samelp")
Norm4Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", Norm4), 
                                               array.array("f", SumNumberUnc), array.array("f", Norm4Unc))
Norm4Graph.SetMarkerStyle(23)
Norm4Graph.SetMarkerSize(2)
Norm4Graph.SetMarkerColor(ROOT.kRed)
Norm4Graph.SetLineWidth(2)
Norm4Graph.SetLineColor(ROOT.kRed)
Norm4Graph.Draw("samelp")
#...Make a legend for this plot...
NormLegend = ROOT.TLegend(0.835,0.755, 0.975,0.975)
NormLegend.SetFillColor(ROOT.kWhite)
NormLegend.SetTextFont(42)
NormLegend.AddEntry(Norm1Graph, "Image 1", "lp")
NormLegend.AddEntry(Norm2Graph, "Image 2", "lp")
NormLegend.AddEntry(Norm3Graph, "Image 3", "lp")
NormLegend.AddEntry(Norm4Graph, "Image 4", "lp")
NormLegend.Draw()
aCanvas.Update()
aCanvas.SaveAs("./PeakNorms.pdf")

#...Now the peak means graphs...
CanvasSetupHisto.GetYaxis().SetTitle("^{55}Fe Peak Mean [ADC Units]")
CanvasSetupHisto.GetYaxis().SetRangeUser(600., 2200.)
CanvasSetupHisto.Draw()
Mean1Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", Mean1), 
                                               array.array("f", SumNumberUnc), array.array("f", Mean1Unc))
Mean1Graph.SetMarkerStyle(20)
Mean1Graph.SetMarkerSize(2)
Mean1Graph.SetMarkerColor(ROOT.kBlack)
Mean1Graph.SetLineWidth(2)
Mean1Graph.SetLineColor(ROOT.kBlack)
Mean1Graph.Draw("samelp")
Mean2Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", Mean2), 
                                               array.array("f", SumNumberUnc), array.array("f", Mean2Unc))
Mean2Graph.SetMarkerStyle(21)
Mean2Graph.SetMarkerSize(2)
Mean2Graph.SetMarkerColor(ROOT.kBlue)
Mean2Graph.SetLineWidth(2)
Mean2Graph.SetLineColor(ROOT.kBlue)
Mean2Graph.Draw("samelp")
Mean3Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", Mean3), 
                                               array.array("f", SumNumberUnc), array.array("f", Mean3Unc))
Mean3Graph.SetMarkerStyle(22)
Mean3Graph.SetMarkerSize(2)
Mean3Graph.SetMarkerColor(ROOT.kGreen - 1)
Mean3Graph.SetLineWidth(2)
Mean3Graph.SetLineColor(ROOT.kGreen - 1)
Mean3Graph.Draw("samelp")
Mean4Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", Mean4), 
                                               array.array("f", SumNumberUnc), array.array("f", Mean4Unc))
Mean4Graph.SetMarkerStyle(23)
Mean4Graph.SetMarkerSize(2)
Mean4Graph.SetMarkerColor(ROOT.kRed)
Mean4Graph.SetLineWidth(2)
Mean4Graph.SetLineColor(ROOT.kRed)
Mean4Graph.Draw("samelp")
#...Make a legend for this plot...
MeanLegend = ROOT.TLegend(0.835,0.155, 0.975,0.375)
MeanLegend.SetFillColor(ROOT.kWhite)
MeanLegend.SetTextFont(42)
MeanLegend.AddEntry(Mean1Graph, "Image 1", "lp")
MeanLegend.AddEntry(Mean2Graph, "Image 2", "lp")
MeanLegend.AddEntry(Mean3Graph, "Image 3", "lp")
MeanLegend.AddEntry(Mean4Graph, "Image 4", "lp")
MeanLegend.Draw()
aCanvas.Update()
aCanvas.SaveAs("./PeakMeans.pdf")
#...Now the peak sigmas graphs...
CanvasSetupHisto.GetYaxis().SetTitle("^{55}Fe Peak Sigma [ADC Units]")
CanvasSetupHisto.GetYaxis().SetRangeUser(150., 350.)
CanvasSetupHisto.Draw()
Sigma1Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", Sigma1), 
                                                array.array("f", SumNumberUnc), array.array("f", Sigma1Unc))
Sigma1Graph.SetMarkerStyle(20)
Sigma1Graph.SetMarkerSize(2)
Sigma1Graph.SetMarkerColor(ROOT.kBlack)
Sigma1Graph.SetLineWidth(2)
Sigma1Graph.SetLineColor(ROOT.kBlack)
Sigma1Graph.Draw("samelp")
Sigma2Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", Sigma2), 
                                                array.array("f", SumNumberUnc), array.array("f", Sigma2Unc))
Sigma2Graph.SetMarkerStyle(21)
Sigma2Graph.SetMarkerSize(2)
Sigma2Graph.SetMarkerColor(ROOT.kBlue)
Sigma2Graph.SetLineWidth(2)
Sigma2Graph.SetLineColor(ROOT.kBlue)
Sigma2Graph.Draw("samelp")
Sigma3Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", Sigma3), 
                                                array.array("f", SumNumberUnc), array.array("f", Sigma3Unc))
Sigma3Graph.SetMarkerStyle(22)
Sigma3Graph.SetMarkerSize(2)
Sigma3Graph.SetMarkerColor(ROOT.kGreen - 1)
Sigma3Graph.SetLineWidth(2)
Sigma3Graph.SetLineColor(ROOT.kGreen - 1)
Sigma3Graph.Draw("samelp")
Sigma4Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", Sigma4), 
                                                array.array("f", SumNumberUnc), array.array("f", Sigma4Unc))
Sigma4Graph.SetMarkerStyle(23)
Sigma4Graph.SetMarkerSize(2)
Sigma4Graph.SetMarkerColor(ROOT.kRed)
Sigma4Graph.SetLineWidth(2)
Sigma4Graph.SetLineColor(ROOT.kRed)
Sigma4Graph.Draw("samelp")
#...Make a legend for this plot...
SigmaLegend = ROOT.TLegend(0.105,0.755, 0.245,0.975)
SigmaLegend.SetFillColor(ROOT.kWhite)
SigmaLegend.SetTextFont(42)
SigmaLegend.AddEntry(Sigma1Graph, "Image 1", "lp")
SigmaLegend.AddEntry(Sigma2Graph, "Image 2", "lp")
SigmaLegend.AddEntry(Sigma3Graph, "Image 3", "lp")
SigmaLegend.AddEntry(Sigma4Graph, "Image 4", "lp")
SigmaLegend.Draw()
aCanvas.Update()
aCanvas.SaveAs("./PeakSigmas.pdf")

# Now, let's  look at the energy resolution.
EnRes1    = []
EnRes2    = []
EnRes3    = []
EnRes4    = []
EnRes1Unc = []
EnRes2Unc = []
EnRes3Unc = []
EnRes4Unc = []
for i in range(len(Mean1)):
  EnRes1.append(Sigma1[i] / Mean1[i])
  EnRes2.append(Sigma2[i] / Mean2[i])
  EnRes3.append(Sigma3[i] / Mean3[i])
  EnRes4.append(Sigma4[i] / Mean4[i])
  EnRes1Unc.append(EnRes1[i] * ((((Mean1Unc[i] / Mean1[i])**2.) + ((Sigma1Unc[i] / Sigma1[i])**2.))**0.5))
  EnRes2Unc.append(EnRes2[i] * ((((Mean2Unc[i] / Mean2[i])**2.) + ((Sigma2Unc[i] / Sigma2[i])**2.))**0.5))
  EnRes3Unc.append(EnRes3[i] * ((((Mean3Unc[i] / Mean3[i])**2.) + ((Sigma3Unc[i] / Sigma3[i])**2.))**0.5))
  EnRes4Unc.append(EnRes4[i] * ((((Mean4Unc[i] / Mean4[i])**2.) + ((Sigma4Unc[i] / Sigma4[i])**2.))**0.5))
#...Now let's actually create and plot the energy resolution graphs...
del CanvasSetupHisto
CanvasSetupHisto = ROOT.TH2D("CanvasSetupHisto", "Plots, plots, plots...", 
                             1, RangeForPlot[0], RangeForPlot[1], 
                             1, 0., 0.45)
CanvasSetupHisto.GetXaxis().SetTitle("Pixel Sum Number")
CanvasSetupHisto.GetYaxis().SetTitle("^{55}Fe Peak Sigma / Mean")
CanvasSetupHisto.GetYaxis().SetTitleOffset(1.0)
CanvasSetupHisto.Draw()
EnRes1Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", EnRes1), 
                                                array.array("f", SumNumberUnc), array.array("f", EnRes1Unc))
EnRes1Graph.SetMarkerStyle(20)
EnRes1Graph.SetMarkerSize(2)
EnRes1Graph.SetMarkerColor(ROOT.kBlack)
EnRes1Graph.SetLineWidth(2)
EnRes1Graph.SetLineColor(ROOT.kBlack)
EnRes1Graph.Draw("samelp")
EnRes2Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", EnRes2), 
                                                array.array("f", SumNumberUnc), array.array("f", EnRes2Unc))
EnRes2Graph.SetMarkerStyle(21)
EnRes2Graph.SetMarkerSize(2)
EnRes2Graph.SetMarkerColor(ROOT.kBlue)
EnRes2Graph.SetLineWidth(2)
EnRes2Graph.SetLineColor(ROOT.kBlue)
EnRes2Graph.Draw("samelp")
EnRes3Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", EnRes3), 
                                                array.array("f", SumNumberUnc), array.array("f", EnRes3Unc))
EnRes3Graph.SetMarkerStyle(22)
EnRes3Graph.SetMarkerSize(2)
EnRes3Graph.SetMarkerColor(ROOT.kGreen - 1)
EnRes3Graph.SetLineWidth(2)
EnRes3Graph.SetLineColor(ROOT.kGreen - 1)
EnRes3Graph.Draw("samelp")
EnRes4Graph = ROOT.TGraphErrors(len(SumNumber), array.array("f", SumNumber),    array.array("f", EnRes4), 
                                                array.array("f", SumNumberUnc), array.array("f", EnRes4Unc))
EnRes4Graph.SetMarkerStyle(23)
EnRes4Graph.SetMarkerSize(2)
EnRes4Graph.SetMarkerColor(ROOT.kRed)
EnRes4Graph.SetLineWidth(2)
EnRes4Graph.SetLineColor(ROOT.kRed)
EnRes4Graph.Draw("samelp")
#...Make a legend for this plot...
EnResLegend = ROOT.TLegend(0.835,0.755, 0.975,0.975)
EnResLegend.SetFillColor(ROOT.kWhite)
EnResLegend.SetTextFont(42)
EnResLegend.AddEntry(EnRes1Graph, "Image 1", "lp")
EnResLegend.AddEntry(EnRes2Graph, "Image 2", "lp")
EnResLegend.AddEntry(EnRes3Graph, "Image 3", "lp")
EnResLegend.AddEntry(EnRes4Graph, "Image 4", "lp")
EnResLegend.Draw()
aCanvas.Update()
aCanvas.SaveAs("./PeakEnRes.pdf")

# Now, read in the sum of five spectra from the root files for each of these images and plot them.
Sum5Spec1File = ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearXray1/noClearXray1_UnShuf.xrayAnalysis.root")
Sum5Spec2File = ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearXray2/noClearXray2_UnShuf.xrayAnalysis.root")
Sum5Spec3File = ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearXray3/noClearXray3_UnShuf.xrayAnalysis.root")
Sum5Spec4File = ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearXray4/noClearXray4_UnShuf.xrayAnalysis.root")
Sum5Spec1 = Sum5Spec1File.Get("PixValHisto_Sum5")
Sum5Spec1.SetLineColor(ROOT.kBlack)
Sum5Spec2 = Sum5Spec2File.Get("PixValHisto_Sum5")
Sum5Spec2.SetLineColor(ROOT.kBlue)
Sum5Spec3 = Sum5Spec3File.Get("PixValHisto_Sum5")
Sum5Spec3.SetLineColor(ROOT.kGreen - 1)
Sum5Spec4 = Sum5Spec4File.Get("PixValHisto_Sum5")
Sum5Spec4.SetLineColor(ROOT.kRed)
# Rebin these puppies because they're kind of noisy...
RebinFactor = 5
for spectrum in [Sum5Spec1, Sum5Spec2, Sum5Spec3, Sum5Spec4]:
  spectrum.SetLineWidth(2)
  spectrum.Rebin(RebinFactor)
  spectrum.Scale(1. / float(RebinFactor))
del CanvasSetupHisto
CanvasSetupHisto = ROOT.TH2D("CanvasSetupHisto", "Plots, plots, plots...", 
                             1, 0., 2900., 
                             1, 0., 14.)
CanvasSetupHisto.GetXaxis().SetTitle("Pixel Value [ADC Units]")
CanvasSetupHisto.GetYaxis().SetTitle("Counts per Bin")
CanvasSetupHisto.GetYaxis().SetTitleOffset(1.0)
CanvasSetupHisto.Draw()
Sum5Spec1.Draw("same")
Sum5Spec2.Draw("same")
Sum5Spec3.Draw("same")
Sum5Spec4.Draw("same")
#...Make a legend for this plot too...
EnResLegend = ROOT.TLegend(0.835,0.755, 0.975,0.975)
EnResLegend.SetFillColor(ROOT.kWhite)
EnResLegend.SetTextFont(42)
EnResLegend.AddEntry(Sum5Spec1, "Image 1", "l")
EnResLegend.AddEntry(Sum5Spec2, "Image 2", "l")
EnResLegend.AddEntry(Sum5Spec3, "Image 3", "l")
EnResLegend.AddEntry(Sum5Spec4, "Image 4", "l")
EnResLegend.Draw()
aCanvas.Update()
aCanvas.SaveAs("./Sum5Spectra.pdf")

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
