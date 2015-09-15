#!/usr/bin/python

####################################################################################################
# Collect the pixel value spectra for the the bevy of dark images we took in the building 2 lab on #
# August 3, 2015.  Look at the noise spectrum in each and see how consistent it is from exposure   #
# to exposure.                                                                                     #
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

# Root files for the pixel value histograms we're going to look at.
RootFiles = []
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearDark1/noClearDark1_UnShuf.DarkFrame.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearDark2/noClearDark2_UnShuf.DarkFrame.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearDark3/noClearDark3_UnShuf.DarkFrame.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearDark4/noClearDark4_UnShuf.DarkFrame.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearDark5/noClearDark5_UnShuf.DarkFrame.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearDark6/noClearDark6_UnShuf.DarkFrame.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearDark7/noClearDark7_UnShuf.DarkFrame.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearDark8/noClearDark8_UnShuf.DarkFrame.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearDark9/noClearDark9_UnShuf.DarkFrame.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/noClearDark10/noClearDark10_UnShuf.DarkFrame.PixelValues.root"))

# List of the descriptive strings for each of the files.
DescrStrings = []
DescrStrings.append("Pixel Values for Dark Image 01")
DescrStrings.append("Pixel Values for Dark Image 02")
DescrStrings.append("Pixel Values for Dark Image 03")
DescrStrings.append("Pixel Values for Dark Image 04")
DescrStrings.append("Pixel Values for Dark Image 05")
DescrStrings.append("Pixel Values for Dark Image 06")
DescrStrings.append("Pixel Values for Dark Image 07")
DescrStrings.append("Pixel Values for Dark Image 08")
DescrStrings.append("Pixel Values for Dark Image 09")
DescrStrings.append("Pixel Values for Dark Image 10")

# A list of root colors for each plot.
PlotColors = []
for i in range(10):
  PlotColors.append(ROOT.kViolet + i)

# Crack open the files and pull out the pixel value histograms.
PixValHistos = []
for i in range(len(RootFiles)):
  PixValHistos.append(RootFiles[i].Get("PixelValueHistoZoom"))
  PixValHistos[i].SetTitle(DescrStrings[i])
  PixValHistos[i].SetLineColor(PlotColors[i])
  PixValHistos[i].SetLineWidth(2)

# OK...  Now, let's save the sum histogram as a png and as a root file...
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
PVBinWidth = PixValHistos[0].GetBinCenter(11) - PixValHistos[0].GetBinCenter(10)
MaxHistoVal = 0.
for pvh in PixValHistos:
  if(pvh.GetMaximum() > MaxHistoVal): MaxHistoVal = pvh.GetMaximum()
CanvasSetupHisto = ROOT.TH2D("CanvasSetupHisto", "Noise/Pedestal Fits", 1,-1000.,1000., 1,0.,1.1*MaxHistoVal)
CanvasSetupHisto.GetXaxis().SetTitle("Background Corrected Pixel Values [ADC Units]")
CanvasSetupHisto.GetYaxis().SetTitle("Counts per " + str(int(PVBinWidth)) + " ADC Unit Bin")
CanvasSetupHisto.Draw()
aCanvas.Update()

# Draw the histograms and make a legend.
for pvh in PixValHistos:
  pvh.Draw("same")
aLegend = ROOT.TLegend(0.895,0.645, 0.975,0.915)
aLegend.SetFillColor(ROOT.kWhite)
aLegend.SetTextFont(42)
aLegend.SetNColumns(2)
for pvh in PixValHistos:
  aLegend.AddEntry(pvh, pvh.GetTitle().split(" ")[-1], "l")
aLegend.Draw()
aCanvas.Update()

# Fit a Gaussian to fit out the with of each noise peak.
FitModels = []
for pvh in PixValHistos:
  FitModels.append(PythonTools.GetOneGausFitModel("FitModel_" + pvh.GetTitle().split(" ")[-1], pvh, 0., 100.))

# Actually do the fit and save the plot.
for i in range(len(PixValHistos)):
  PixValHistos[i].Fit(FitModels[i], "QLLEM", "", -400., 200.)
aCanvas.Update()
OutputPlotName = "/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-03/DarkFrameValues.pdf"
aCanvas.SaveAs(OutputPlotName)

# Report the means and sigmas for each of the fits.
print "\tImage\tMean [ADC Units]\tSigma [ADC Units]\tChi^2 / NDF (P. Val.)"
for i in range(len(FitModels)):
  print "\t", DescrStrings[i].split(" ")[-1] + "\t", "{:1.3f}".format(FitModels[i].GetParameter(2)), "+/-", "{:1.3f}".format(FitModels[i].GetParError(2)), "\t", "{:1.3f}".format(FitModels[i].GetParameter(3)), "+/-", "{:1.3f}".format(FitModels[i].GetParError(3)), "\t", "{:0.3f}".format(FitModels[i].GetChisquare()), "/", FitModels[i].GetNDF(), "=", "{:0.3f}".format(FitModels[i].GetChisquare() / float(FitModels[i].GetNDF())), "(" + "{:0.6f}".format(FitModels[i].GetProb()) + ")"

# Save the histograms and their fit functions to a root file
OutputFile = ROOT.TFile(OutputPlotName.replace("pdf", "root"), "recreate")
for pvh in PixValHistos:
  pvh.Write()
for fm in FitModels:
  fm.Write()
OutputFile.Close()

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
