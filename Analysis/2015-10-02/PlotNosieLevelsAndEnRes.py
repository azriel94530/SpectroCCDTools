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

# VDD values for each exposure:
VDD = [17., 19., 21., 23.]

# Noise peak sigmas:
NoiseSigm = [16.54, 42.43, 83.20, 120.0]

# X ray peak mean and sigma values
XRayMean = [1., 1., 1750., 1950.]
XRaySigm = [1., 1., 392.8, 581.8]
ERes = []
for i in range(len(XRayMean)):
  ERes.append(XRaySigm[i] / XRayMean[i])

# Make some TGraph objects for these data.
MarkerSize = 3
# First the means...
NoiseSigmGraph = ROOT.TGraph(len(VDD), array.array("f", VDD), array.array("f", NoiseSigm))
NoiseSigmGraph.SetMarkerStyle(20)
NoiseSigmGraph.SetMarkerSize(MarkerSize)
NoiseSigmGraph.SetMarkerColor(ROOT.kBlack)
NoiseSigmGraph.SetLineColor(ROOT.kBlack)
NoiseSigmGraph.GetXaxis().SetTitle("V_{DD} [V]")
NoiseSigmGraph.GetYaxis().SetTitle("Noise Value [ADC Units]")
EResGraph = ROOT.TGraph(len(VDD), array.array("f", VDD), array.array("f", ERes))
EResGraph.SetMarkerStyle(21)
EResGraph.SetMarkerSize(MarkerSize)
EResGraph.SetMarkerColor(ROOT.kBlue)
EResGraph.SetLineColor(ROOT.kBlue)
EResGraph.GetXaxis().SetTitle("V_{DD} [V]")
EResGraph.GetYaxis().SetTitle("Energy Resolution")


# Get ready to plot things!
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.08)
aPad.SetRightMargin(0.02)
aPad.SetBottomMargin(0.09)
aPad.SetTopMargin(0.02)
aPad.SetLogy(0)
aPad.Draw()
aPad.cd()
ROOT.gStyle.SetOptTitle(0)

# Plot these things...
NoiseSigmGraph.Draw("alp")
aCanvas.Update()
aCanvas.SaveAs("VDDScan_Noise.pdf")
EResGraph.Draw("alp")
aCanvas.Update()
aCanvas.SaveAs("VDDScan_ERes.pdf")

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
