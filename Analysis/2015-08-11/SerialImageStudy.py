#!/usr/bin/python

####################################################################################################
# Collect the pixel value spectra for the serial images we looked at in the ALS staging area. Then #
# add them up. Do some fits to the pedestal/noise region of all four (the individual images and    #
# the sum), draw the spectra and fits, then report the results.                                    #
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
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/Dark_Serial_1/Dark_Serial_1_UnShuf.NoiseStudy.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/Dark_Serial_2/Dark_Serial_2_UnShuf.NoiseStudy.PixelValues.root"))
RootFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/Dark_Serial_3/Dark_Serial_3_UnShuf.NoiseStudy.PixelValues.root"))

# List of the descriptive strings for each of the files.
DescrStrings = []
DescrStrings.append("1  ")
DescrStrings.append("2  ")
DescrStrings.append("3  ")
DescrStrings.append("Sum")

# A list of root colors for each plot.
PlotColors = [ROOT.kBlack, ROOT.kBlue, ROOT.kGreen - 1, ROOT.kRed]

# Crack open the files and pull out the pixel value histograms.
PixValHistos = []
for i in range(len(RootFiles)):
  PixValHistos.append(RootFiles[i].Get("PixelValueHistoZoom"))
  PixValHistos[i].SetTitle(DescrStrings[i])
  PixValHistos[i].SetLineColor(PlotColors[i])
  PixValHistos[i].SetLineWidth(2)

# Construct the sum histogram
Image1File = ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/Dark_Serial_1/Dark_Serial_1_UnShuf.root")
Image2File = ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/Dark_Serial_2/Dark_Serial_2_UnShuf.root")
Image3File = ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/Dark_Serial_3/Dark_Serial_3_UnShuf.root")
Image1Hist = Image1File.Get("thatHistogram")
Image2Hist = Image2File.Get("thatHistogram")
Image3Hist = Image3File.Get("thatHistogram")
SumHist = ROOT.TH2D("SumHist", "SumHistogram",
                    Image1Hist.GetXaxis().GetNbins(), Image1Hist.GetXaxis().GetXmin(), Image1Hist.GetXaxis().GetXmax(),
                    Image1Hist.GetYaxis().GetNbins(), Image1Hist.GetYaxis().GetXmin(), Image1Hist.GetYaxis().GetXmax())
SumHist.GetXaxis().SetTitle(Image1Hist.GetXaxis().GetTitle())
SumHist.GetYaxis().SetTitle(Image1Hist.GetYaxis().GetTitle())
SumHist.GetXaxis().SetTitleOffset(Image1Hist.GetXaxis().GetTitleOffset())
SumHist.GetYaxis().SetTitleOffset(Image1Hist.GetYaxis().GetTitleOffset())
SumHist.Add(Image1Hist, 1.)
SumHist.Add(Image2Hist, 1.)
SumHist.Add(Image3Hist, 1.)

# Take the sum histogram, and create a pixel value histogram from it.
xLo =  0.5 
xHi = 12. 
yLo =  1. 
yHi = 27.
SumHist.GetXaxis().SetRangeUser(xLo, xHi)
SumHist.GetYaxis().SetRangeUser(yLo, yHi)
Xbins = range(SumHist.GetXaxis().FindBin(xLo), SumHist.GetXaxis().FindBin(xHi))
Ybins = range(SumHist.GetYaxis().FindBin(yLo), SumHist.GetYaxis().FindBin(yHi))
print "\tMaking a pixel value histogram from the summed image..."
PixelValues = []
nValues = len(Xbins) * len(Ybins)
iVal = 0
for xbin in Xbins:
  for ybin in Ybins:
    PixelValues.append(SumHist.GetBinContent(xbin, ybin))
    iVal += 1
    if((nValues >= 100) and (iVal % int(nValues / 100) == 0)):
      ROOT.StatusBar(iVal, nValues, int(nValues / 100))
print
PixValLo = round(min(PixelValues), -3)
PixValHi = round(max(PixelValues), -3)
PixValBW = 20.
nBins = 0
thisBinVal = PixValLo
while(thisBinVal < PixValHi):
  nBins += 1
  thisBinVal = PixValLo + (float(nBins) * PixValBW)
SumImagePixelValueHisto = ROOT.TH1D("SumImagePixelValueHisto", "Sum", nBins, PixValLo, thisBinVal)
SumImagePixelValueHisto.GetXaxis().SetTitle("Background Corrected Pixel Values [ADC Units]")
SumImagePixelValueHisto.GetXaxis().SetTitleOffset(1.1)
TitleString = "Counts per " + "{:0.1f}".format(PixValBW) + " ADC Unit Bin"
SumImagePixelValueHisto.GetYaxis().SetTitle(TitleString)
SumImagePixelValueHisto.GetYaxis().SetTitleOffset(1.2)
SumImagePixelValueHisto.SetLineColor(PlotColors[-1])
SumImagePixelValueHisto.SetLineWidth(2)
for val in PixelValues: SumImagePixelValueHisto.Fill(val)
PixValHistos.append(SumImagePixelValueHisto)

# OK...  Now, let's save the sum histogram as a png and as a root file...
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.05)
aPad.SetBottomMargin(0.08)
aPad.Draw()
aPad.cd()
SumHist.Draw("colz")
aCanvas.SaveAs("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/NoiseStudy/SerialDarkSum.png")
SumHistRootFile = ROOT.TFile("../Images/2015-08-11/NoiseStudy/SerialDarkSum.root", "recreate")
SumHist.Write()
SumHistRootFile.Close()

# Next, let's do the pixel value histograms.
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
CanvasSetupHisto = ROOT.TH2D("CanvasSetupHisto", "Noise/Pedestal Fits", 1,-1000.,1000., 1,0.,1.1*MaxHistoVal)
CanvasSetupHisto.GetXaxis().SetTitle("Background Corrected Pixel Values [ADC Units]")
CanvasSetupHisto.GetYaxis().SetTitle("Counts per Bin")
CanvasSetupHisto.Draw()

# Draw the histograms and make a legend.
for pvh in PixValHistos:
  pvh.Draw("same")
aLegend = ROOT.TLegend(0.895,0.645, 0.975,0.915)
aLegend.SetFillColor(ROOT.kWhite)
aLegend.SetTextFont(42)
for pvh in PixValHistos:
  aLegend.AddEntry(pvh, pvh.GetTitle(), "l")
aLegend.Draw()
# Fit a Gaussian to fit out the with of the noise peak.
FitModels = []
FitModels.append(PythonTools.GetOneGausFitModel("FitModel_1",   PixValHistos[0], 0., 100.))
FitModels.append(PythonTools.GetOneGausFitModel("FitModel_2",   PixValHistos[1], 0., 100.))
FitModels.append(PythonTools.GetOneGausFitModel("FitModel_3",   PixValHistos[2], 0., 100.))
FitModels.append(PythonTools.GetOneGausFitModel("FitModel_Sum", PixValHistos[3], 0., 200.))

# Actually do the fit and save the plot.
for i in range(len(PixValHistos)):
  PixValHistos[i].Fit(FitModels[i], "QLLEM", "", -400., 400.)
aCanvas.Update()
aCanvas.SaveAs("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/NoiseStudy/SerialImages.pdf")

# Report the means and sigmas for each of the fits.
print "\tImage\tMean [ADC Units]\tSigma [ADC Units]"
for i in range(len(FitModels)):
  print "\t", DescrStrings[i] + "\t", "{:1.3f}".format(FitModels[i].GetParameter(2)), "+/-", "{:1.3f}".format(FitModels[i].GetParError(2)), "\t", "{:1.3f}".format(FitModels[i].GetParameter(3)), "+/-", "{:1.3f}".format(FitModels[i].GetParError(3))

# Save the histograms and their fit functions to a root file
OutputFile = ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-08-11/NoiseStudy/SerialImages.root", "recreate")
for pvh in PixValHistos:
  pvh.Write()
for fm in FitModels:
  fm.Write()
OutputFile.Close()

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
