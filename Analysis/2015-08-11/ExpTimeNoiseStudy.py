#!/usr/bin/python

####################################################################################################
# Collect the pixel value spectra for the different exposure times we looked at in the ALS staging #
# area.  Do some fits to the pedestal/noise region, draw the spectra and fits, then report the     #
# results.                                                                                         #
####################################################################################################

# Header, import statements etc.
import time
import sys
import ROOT
import numpy
import array
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

# Root files for the pixel value histograms we're going to look at.
RootFiles = []
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/Dark_100x30000/Dark_100x30000_UnShuf.NoiseStudy.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/Dark_500x30000/Dark_500x30000_UnShuf.NoiseStudy.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/Dark_1000x30000/Dark_1000x30000_UnShuf.NoiseStudy.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/Dark_1500x30000_HeaterNotRunning/Dark_1500x30000_HeaterNotRunning_UnShuf.NoiseStudy.PixelValues.root"))

# List of the exposure times for each of the files.
Exptimes = [2, 10, 19, 28] #[seconds]

# A list of root colors for each plot.
PlotColors = [ROOT.kBlack, ROOT.kBlue, ROOT.kGreen - 1, ROOT.kRed]

# Crack open the files and pull out the pixel value histograms.
PixValHistos = []
for i in range(len(RootFiles)):
  PixValHistos.append(RootFiles[i].Get("PixelValueHistoZoom"))
  PixValHistos[i].SetTitle(str(Exptimes[i]) + " Seconds")
  PixValHistos[i].SetLineColor(PlotColors[i])
  PixValHistos[i].SetLineWidth(2)

# A nice canvas and pad on which to plot things...
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.07)
aPad.SetRightMargin(0.02)
aPad.SetBottomMargin(0.08)
aPad.SetLogy(0)
aPad.Draw()
aPad.cd()

# And a simple TH2D to set it up...
MaxHistoVal = 0.
for pvh in PixValHistos:
  if(pvh.GetMaximum() > MaxHistoVal): MaxHistoVal = pvh.GetMaximum()
CanvasSetupHisto = ROOT.TH2D("CanvasSetupHisto", "Noise/Pedestal Fits", 1,-500.,500., 1,0.,1.1*MaxHistoVal)
CanvasSetupHisto.GetXaxis().SetTitle("Background Corrected Pixel Values [ADC Units]")
CanvasSetupHisto.GetYaxis().SetTitle("Counts per Bin")
CanvasSetupHisto.Draw()

# Draw the histograms and make a legend.
for pvh in PixValHistos:
  pvh.Draw("same")
aLegend = ROOT.TLegend(0.75,0.645, 0.975,0.915)
aLegend.SetFillColor(ROOT.kWhite)
aLegend.SetTextFont(42)
for pvh in PixValHistos:
  aLegend.AddEntry(pvh, pvh.GetTitle(), "l")
aLegend.Draw()
# Fit a Gaussian to fit out the with of the noise peak.
FitModels = []
FitModels.append(PythonTools.GetOneGausFitModel("FitModel_" + str(Exptimes[0]) + "_sec", PixValHistos[0], 0., 100.))
FitModels.append(PythonTools.GetOneGausFitModel("FitModel_" + str(Exptimes[1]) + "_sec", PixValHistos[1], 0., 100.))
FitModels.append(PythonTools.GetOneGausFitModel("FitModel_" + str(Exptimes[2]) + "_sec", PixValHistos[2], 0., 100.))
FitModels.append(PythonTools.GetOneGausFitModel("FitModel_" + str(Exptimes[3]) + "_sec", PixValHistos[3], 0., 100.))

# Actually do the fit and save the plot.
for i in range(len(PixValHistos)):
  PixValHistos[i].Fit(FitModels[i], "QLLEM", "", -400., 400.)
aCanvas.Update()
aCanvas.SaveAs("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/NoiseStudy/ExpTimeStudy.pdf")

# Report the means and sigmas for each of the fits.
print "\tExp. Time [s]\tMean [ADC Units]\tSigma [ADC Units]"
for i in range(len(FitModels)):
  print "\t", Exptimes[i], "\t\t", "{:1.3f}".format(FitModels[i].GetParameter(2)), "+/-", "{:1.3f}".format(FitModels[i].GetParError(2)), "\t", "{:1.3f}".format(FitModels[i].GetParameter(3)), "+/-", "{:1.3f}".format(FitModels[i].GetParError(3))

# Save the histograms and their fit functions to a root file
OutputFile = ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/NoiseStudy/ExpTimeStudy.root", "recreate")
for pvh in PixValHistos:
  pvh.Write()
for fm in FitModels:
  fm.Write()
OutputFile.Close()

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
