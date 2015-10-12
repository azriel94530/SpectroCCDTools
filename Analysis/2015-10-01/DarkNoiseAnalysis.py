#!/usr/bin/python

####################################################################################################
# Look at the dark noise data that Sufia took on October 1, 2015.  She scanned through several     #
# values of both VDD and Vsub.                                                                     #
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

def PrintMeanAndRMSofImage(histo):
  nBinsX = histo.GetXaxis().GetNbins()
  nBinsY = histo.GetYaxis().GetNbins()
  PVAverage   = 0.
  PVSqAverage = 0.
  for xBin in range(nBinsX):
    for yBin in range(nBinsY):
      PVAverage   += histo.GetBinContent(xBin, yBin)
      PVSqAverage += (histo.GetBinContent(xBin, yBin))**2.
  PVAverage   /= float(nBinsX * nBinsY)
  PVSqAverage /= float(nBinsX * nBinsY)
  PVRMS = (PVSqAverage - (PVAverage**2.))**0.5
  print "\tAverage Value of", histo.GetName(), "=", "{:0.1f}".format(PVAverage), "+/-", "{:0.1f}".format(PVRMS)
  return PVAverage, PVRMS

def MakePVHisto(imagehisto):
  Xbins = range(imagehisto.GetXaxis().GetNbins())
  Ybins = range(imagehisto.GetYaxis().GetNbins())
  print "\tMaking a pixel value histogram from", imagehisto.GetName() + "..."
  PixelValues = []
  nValues = len(Xbins) * len(Ybins)
  iVal = 0
  for xbin in Xbins:
    for ybin in Ybins:
      PixelValues.append(imagehisto.GetBinContent(xbin, ybin))
      iVal += 1
      if((nValues >= 100) and (iVal % int(nValues / 100) == 0)):
        ROOT.StatusBar(iVal, nValues, int(nValues / 100))
  print
  PixValLo = -999.#round(min(PixelValues), -3)
  PixValHi =  999.#round(max(PixelValues), -3)
  PixValBW = 10.
  nBins = 0
  thisBinVal = PixValLo
  while(thisBinVal < PixValHi):
    nBins += 1
    thisBinVal = PixValLo + (float(nBins) * PixValBW)
  PVHisto = ROOT.TH1D(imagehisto.GetName() + "_PixVals", "Pixel Values for " + imagehisto.GetName(), nBins, PixValLo, thisBinVal)
  PVHisto.GetXaxis().SetTitle("Background Corrected Pixel Values [ADC Units]")
  PVHisto.GetXaxis().SetTitleOffset(1.1)
  TitleString = "Counts per " + "{:0.1f}".format(PixValBW) + " ADC Unit Bin"
  PVHisto.GetYaxis().SetTitle(TitleString)
  PVHisto.GetYaxis().SetTitleOffset(1.2)
  PVHisto.SetLineColor(ROOT.kBlue)
  PVHisto.SetLineWidth(2)
  for val in PixelValues: PVHisto.Fill(val)
  return PVHisto

def DoDarkNoiseAnalysis(histo, fitmodel):
  histo.Draw()
  histo.Fit(fitmodel, "QLLEM", "", -150., 150.)
  ReportBox = ROOT.TPaveText(0.677,0.62,0.977,0.90,"blNDC")
  ReportBox.SetName("ReportBox")
  ReportBox.SetBorderSize(1)
  ReportBox.SetFillColor(ROOT.kWhite)
  ReportBox.AddText("Mean  = " + "{:2.3f}".format(GausFitModel.GetParameter(2)) + " #pm " + "{:2.3f}".format(GausFitModel.GetParError(2)))
  ReportBox.AddText("Sigma = " + "{:2.3f}".format(GausFitModel.GetParameter(3)) + " #pm " + "{:2.3f}".format(GausFitModel.GetParError(3)))
  ReportBox.AddText("#chi^{2} / NDF = " + "{:2.3f}".format(GausFitModel.GetChisquare()) + " / " + "{:2.3f}".format(GausFitModel.GetNDF()) + " = " + "{:2.3f}".format(GausFitModel.GetChisquare() / float(GausFitModel.GetNDF())))
  ReportBox.AddText("P-Value = " + "{:1.9f}".format(GausFitModel.GetProb()))
  ReportBox.Draw()
  aCanvas.Update()
  aCanvas.SaveAs(OutputFileDirectory + histo.GetName() + ".pdf")
  return [GausFitModel.GetParameter(2), GausFitModel.GetParError(2), GausFitModel.GetParameter(3), GausFitModel.GetParError(3)]

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

# Root files for the image histograms.
VDDScanImageFiles = []
VDDScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD17V_1/imageVDD17V_1_UnShuf.root"))
VDDScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD17V_2/imageVDD17V_2_UnShuf.root"))
VDDScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_1/imageVDD18V_1_UnShuf.root"))
VDDScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_2/imageVDD18V_2_UnShuf.root"))
VDDScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD19V_1/imageVDD19V_1_UnShuf.root"))
VDDScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD19V_2/imageVDD19V_2_UnShuf.root"))
VDDScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD20V_1/imageVDD20V_1_UnShuf.root"))
VDDScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD20V_2/imageVDD20V_2_UnShuf.root"))
VDDValues = [17., 17., 18., 18., 19., 19., 20., 20.]
#print len(VDDScanImageFiles), len(VDDValues)

VSubScanImageFiles = []
VSubScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_1/imageVDD18V_1_UnShuf.root"))
VSubScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_2/imageVDD18V_2_UnShuf.root"))
VSubScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_Vsub60V_1/imageVDD18V_Vsub60V_1_UnShuf.root"))
VSubScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_Vsub60V_2/imageVDD18V_Vsub60V_2_UnShuf.root"))
VSubScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_Vsub70V_1/imageVDD18V_Vsub70V_1_UnShuf.root"))
VSubScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_Vsub70V_2/imageVDD18V_Vsub70V_2_UnShuf.root"))
VSubScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_Vsub80V_1/imageVDD18V_Vsub80V_1_UnShuf.root"))
VSubScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_Vsub80V_2/imageVDD18V_Vsub80V_2_UnShuf.root"))
VSubScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_Vsub90V_1/imageVDD18V_Vsub90V_1_UnShuf.root"))
VSubScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_Vsub90V_2/imageVDD18V_Vsub90V_2_UnShuf.root"))
VSubScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_Vsub100V_1/imageVDD18V_Vsub100V_1_UnShuf.root"))
VSubScanImageFiles.append(ROOT.TFile("/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/imageVDD18V_Vsub100V_2/imageVDD18V_Vsub100V_2_UnShuf.root"))
VSubValues = [50., 50., 60., 60., 70., 70., 80., 80., 90., 90., 100., 100.]
#print len(VSubScanImageFiles), len(VSubValues)

# Pull in the image histograms out of each one of the files we just opened.
VDDScanImages = []
FileNumber = 0
for rootfile in VDDScanImageFiles:
  VDDScanImages.append(rootfile.Get("thatHistogram"))
  if(VDDValues[FileNumber - 1] == VDDValues[FileNumber]):
    ImageNumber = 2
  else:
    ImageNumber = 1
  VDDScanImages[FileNumber].SetName("VDDScanImages_VDD" + str(VDDValues[FileNumber]) + "_" + str(ImageNumber))
  #print VDDScanImages[FileNumber].GetName()
  FileNumber += 1

VSubScanImages = []
FileNumber = 0
for rootfile in VSubScanImageFiles:
  VSubScanImages.append(rootfile.Get("thatHistogram"))
  if(VSubValues[FileNumber - 1] == VSubValues[FileNumber]):
    ImageNumber = 2
  else:
    ImageNumber = 1
  VSubScanImages[FileNumber].SetName("VSubScanImages_Vsub" + str(VSubValues[FileNumber]) + "_" + str(ImageNumber))
  #print VSubScanImages[FileNumber].GetName()
  FileNumber += 1

# Create a canvas and a pad to draw these things on...
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.07)
aPad.SetBottomMargin(0.08)
aPad.SetRightMargin(0.02)
aPad.SetTopMargin(0.02)
aPad.Draw()
aPad.cd()
ROOT.gStyle.SetOptTitle(0)
OutputFileDirectory = "/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-01_dark/Analysis/"

# Now, create a pixel value histogram for each of the image histograms, and fit out the mean and width.
# VDD Scan...
VDDScanPVHistos = []
for imagehisto in VDDScanImages:
  VDDScanPVHistos.append(MakePVHisto(imagehisto))
GausFitModel = PythonTools.GetOneGausFitModel("GausFitModel", VDDScanPVHistos[0], 0., 50.)
VDDScanMeans = []
VDDScanMeUns = []
VDDScanSigmas = []
VDDScanSigUns = []
Zeros = []
for histo in VDDScanPVHistos:
  thisResult = DoDarkNoiseAnalysis(histo, GausFitModel)
  VDDScanMeans.append(thisResult[0])
  VDDScanMeUns.append(thisResult[1])
  VDDScanSigmas.append(thisResult[2])
  VDDScanSigUns.append(thisResult[3])
  Zeros.append(0.)
VDDScanMeanGraph = ROOT.TGraphErrors(len(VDDValues), array.array("f", VDDValues), array.array("f", VDDScanMeans),
                                                     array.array("f", Zeros),     array.array("f", VDDScanMeUns))
VDDScanMeanGraph.SetName("VDDScanMeanGraph")
VDDScanMeanGraph.GetXaxis().SetTitle("V_{DD} Value [V]")
VDDScanMeanGraph.GetYaxis().SetTitle("Noise Peak Mean Value [ADC Units]")
VDDScanMeanGraph.SetMarkerStyle(20)
VDDScanMeanGraph.SetMarkerColor(ROOT.kBlack)
VDDScanSigmaGraph = ROOT.TGraphErrors(len(VDDValues), array.array("f", VDDValues), array.array("f", VDDScanSigmas),
                                                      array.array("f", Zeros),     array.array("f", VDDScanSigUns))
VDDScanSigmaGraph.SetName("VDDScanSigmaGraph")
VDDScanSigmaGraph.GetXaxis().SetTitle("V_{DD} Value [V]")
VDDScanSigmaGraph.GetYaxis().SetTitle("Noise Peak Sigma Value [ADC Units]")
VDDScanSigmaGraph.SetMarkerStyle(21)
VDDScanSigmaGraph.SetMarkerColor(ROOT.kBlack)
# Vsub Scan...
VSubScanPVHistos = []
for imagehisto in VSubScanImages:
  VSubScanPVHistos.append(MakePVHisto(imagehisto))
GausFitModel = PythonTools.GetOneGausFitModel("GausFitModel", VSubScanPVHistos[0], 0., 50.)
VSubScanMeans = []
VSubScanMeUns = []
VSubScanSigmas = []
VSubScanSigUns = []
Zeros = []
for histo in VSubScanPVHistos:
  thisResult = DoDarkNoiseAnalysis(histo, GausFitModel)
  VSubScanMeans.append(thisResult[0])
  VSubScanMeUns.append(thisResult[1])
  VSubScanSigmas.append(thisResult[2])
  VSubScanSigUns.append(thisResult[3])
  Zeros.append(0.)
VSubScanMeanGraph = ROOT.TGraphErrors(len(VSubValues), array.array("f", VSubValues), array.array("f", VSubScanMeans),
                                                       array.array("f", Zeros),      array.array("f", VSubScanMeUns))
VSubScanMeanGraph.SetName("VSubScanMeanGraph")
VSubScanMeanGraph.GetXaxis().SetTitle("V_{sub} Value [V]")
VSubScanMeanGraph.GetYaxis().SetTitle("Noise Peak Mean Value [ADC Units]")
VSubScanMeanGraph.SetMarkerStyle(20)
VSubScanMeanGraph.SetMarkerColor(ROOT.kBlue)
VSubScanSigmaGraph = ROOT.TGraphErrors(len(VSubValues), array.array("f", VSubValues), array.array("f", VSubScanSigmas),
                                                        array.array("f", Zeros),      array.array("f", VSubScanSigUns))
VSubScanSigmaGraph.SetName("VSubScanSigmaGraph")
VSubScanSigmaGraph.GetXaxis().SetTitle("V_{sub} Value [V]")
VSubScanSigmaGraph.GetYaxis().SetTitle("Noise Peak Sigma Value [ADC Units]")
VSubScanSigmaGraph.SetMarkerStyle(21)
VSubScanSigmaGraph.SetMarkerColor(ROOT.kBlue)

for graph in [VDDScanMeanGraph, VDDScanSigmaGraph, VSubScanMeanGraph, VSubScanSigmaGraph]:
  graph.GetYaxis().SetTitleOffset(0.8)
  graph.SetMarkerSize(3)
  graph.Draw("ap")
  aCanvas.SaveAs("./" + graph.GetName() + ".pdf")

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
