#!/usr/bin/python

####################################################################################################
# Perform a detailed analysis of the dark images taken in the building 2 lab on September 23,      #
# 2015.  This will happen in two stages.  First, we will take each group of five dark images and   #
# subtract them from each other to see what the difference images look like.  Second, we will make #
# a histogram of all the pixel values for each of them to look at the noise levels.                #
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
LightsOnFiles = []
LightsOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOn1/LightsOn1_UnShuf.root"))
LightsOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOn2/LightsOn2_UnShuf.root"))
LightsOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOn3/LightsOn3_UnShuf.root"))
LightsOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOn4/LightsOn4_UnShuf.root"))
LightsOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOn5/LightsOn5_UnShuf.root"))
CoverOnFiles = []
CoverOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/CoverOn1/CoverOn1_UnShuf.root"))
CoverOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/CoverOn2/CoverOn2_UnShuf.root"))
CoverOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/CoverOn3/CoverOn3_UnShuf.root"))
CoverOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/CoverOn4/CoverOn4_UnShuf.root"))
CoverOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/CoverOn5/CoverOn5_UnShuf.root"))
LightsOffCoverOnFiles = []
LightsOffCoverOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOffCoverOn1/LightsOffCoverOn1_UnShuf.root"))
LightsOffCoverOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOffCoverOn2/LightsOffCoverOn2_UnShuf.root"))
LightsOffCoverOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOffCoverOn3/LightsOffCoverOn3_UnShuf.root"))
LightsOffCoverOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOffCoverOn4/LightsOffCoverOn4_UnShuf.root"))
LightsOffCoverOnFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOffCoverOn5/LightsOffCoverOn5_UnShuf.root"))
LightsOffFiles = []
LightsOffFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOff1/LightsOff1_UnShuf.root"))
LightsOffFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOff2/LightsOff2_UnShuf.root"))
LightsOffFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOff3/LightsOff3_UnShuf.root"))
LightsOffFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOff4/LightsOff4_UnShuf.root"))
LightsOffFiles.append(ROOT.TFile("/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/LightsOff5/LightsOff5_UnShuf.root"))

# Pull in the image histograms out of each one of the files we just opened.
LightsOnImages = []
FileNumber = 1
for rootfile in LightsOnFiles:
  LightsOnImages.append(rootfile.Get("thatHistogram"))
  LightsOnImages[-1].SetName("LightsOn_" + str(FileNumber))
  FileNumber += 1
CoverOnImages = []
FileNumber = 1
for rootfile in CoverOnFiles:
  CoverOnImages.append(rootfile.Get("thatHistogram"))
  CoverOnImages[-1].SetName("CoverOn_" + str(FileNumber))
  FileNumber += 1
LightsOffCoverOnImages = []
FileNumber = 1
for rootfile in LightsOffCoverOnFiles:
  LightsOffCoverOnImages.append(rootfile.Get("thatHistogram"))
  LightsOffCoverOnImages[-1].SetName("LightsOffCoverOn_" + str(FileNumber))
  FileNumber += 1
LightsOffImages = []
FileNumber = 1
for rootfile in LightsOffFiles:
  LightsOffImages.append(rootfile.Get("thatHistogram"))
  LightsOffImages[-1].SetName("LightsOff_" + str(FileNumber))
  FileNumber += 1

# Create a canvas and a pad to draw these things on...
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.05)
aPad.SetBottomMargin(0.08)
aPad.Draw()
aPad.cd()
OutputFileDirectory = "/Users/vmgehman/Documents/CCDDevelopment/SpectroCCD/Images/2015-09-23/Analysis/"

# Create subtraction images for all five images in each of the four data sets.
NImages = 5
NBinsX = LightsOnImages[0].GetXaxis().GetNbins()
XLo = LightsOnImages[0].GetXaxis().GetXmin()
XHi = LightsOnImages[0].GetXaxis().GetXmax()
XTitle = LightsOnImages[0].GetXaxis().GetTitle()
XTOfst = LightsOnImages[0].GetXaxis().GetTitleOffset()
NBinsY = LightsOnImages[0].GetYaxis().GetNbins()
YLo = LightsOnImages[0].GetYaxis().GetXmin()
YHi = LightsOnImages[0].GetYaxis().GetXmax()
YTitle = LightsOnImages[0].GetYaxis().GetTitle()
YTOfst = LightsOnImages[0].GetYaxis().GetTitleOffset()

LightsOnSubtrImages = []
PixelValueHalfRange = 50.
for i in range(NImages):
  for j in range(i + 1, NImages):
    HistName = "LightsOn_" + str(i) + "-" + str(j)
    HistTitl = "Subtraction histogram for LightsOn " + str(i) + " - " + str(j)
    LightsOnSubtrImages.append(ROOT.TH2D(HistName, HistTitl, NBinsX, XLo, XHi, NBinsY, YLo, YHi))
    LightsOnSubtrImages[-1].GetXaxis().SetTitle(XTitle)
    LightsOnSubtrImages[-1].GetXaxis().SetTitleOffset(XTOfst)
    LightsOnSubtrImages[-1].GetYaxis().SetTitle(YTitle)
    LightsOnSubtrImages[-1].GetYaxis().SetTitleOffset(YTOfst)
    LightsOnSubtrImages[-1].Add(LightsOnImages[i],  1.)
    LightsOnSubtrImages[-1].Add(LightsOnImages[j], -1.)
    LightsOnSubtrImages[-1].GetZaxis().SetRangeUser(-1. * PixelValueHalfRange, PixelValueHalfRange)
    LightsOnSubtrImages[-1].Draw("colz")
    aCanvas.Update()
    aCanvas.SaveAs(OutputFileDirectory + HistName + ".png")

CoverOnSubtrImages = []
for i in range(NImages):
  for j in range(i + 1, NImages):
    HistName = "CoverOn_" + str(i) + "-" + str(j)
    HistTitl = "Subtraction histogram for CoverOn " + str(i) + " - " + str(j)
    CoverOnSubtrImages.append(ROOT.TH2D(HistName, HistTitl, NBinsX, XLo, XHi, NBinsY, YLo, YHi))
    CoverOnSubtrImages[-1].GetXaxis().SetTitle(XTitle)
    CoverOnSubtrImages[-1].GetXaxis().SetTitleOffset(XTOfst)
    CoverOnSubtrImages[-1].GetYaxis().SetTitle(YTitle)
    CoverOnSubtrImages[-1].GetYaxis().SetTitleOffset(YTOfst)
    CoverOnSubtrImages[-1].Add(CoverOnImages[i],  1.)
    CoverOnSubtrImages[-1].Add(CoverOnImages[j], -1.)
    CoverOnSubtrImages[-1].GetZaxis().SetRangeUser(-1. * PixelValueHalfRange, PixelValueHalfRange)
    CoverOnSubtrImages[-1].Draw("colz")
    aCanvas.Update()
    aCanvas.SaveAs(OutputFileDirectory + HistName + ".png")
LightsOffCoverOnSubtrImages = []
for i in range(NImages):
  for j in range(i + 1, NImages):
    HistName = "LightsOffCoverOn_" + str(i) + "-" + str(j)
    HistTitl = "Subtraction histogram for LightsOffCoverOn " + str(i) + " - " + str(j)
    LightsOffCoverOnSubtrImages.append(ROOT.TH2D(HistName, HistTitl, NBinsX, XLo, XHi, NBinsY, YLo, YHi))
    LightsOffCoverOnSubtrImages[-1].GetXaxis().SetTitle(XTitle)
    LightsOffCoverOnSubtrImages[-1].GetXaxis().SetTitleOffset(XTOfst)
    LightsOffCoverOnSubtrImages[-1].GetYaxis().SetTitle(YTitle)
    LightsOffCoverOnSubtrImages[-1].GetYaxis().SetTitleOffset(YTOfst)
    LightsOffCoverOnSubtrImages[-1].Add(LightsOffCoverOnImages[i],  1.)
    LightsOffCoverOnSubtrImages[-1].Add(LightsOffCoverOnImages[j], -1.)
    LightsOffCoverOnSubtrImages[-1].GetZaxis().SetRangeUser(-1. * PixelValueHalfRange, PixelValueHalfRange)
    LightsOffCoverOnSubtrImages[-1].Draw("colz")
    aCanvas.Update()
    aCanvas.SaveAs(OutputFileDirectory + HistName + ".png")
LightsOffSubtrImages = []
for i in range(NImages):
  for j in range(i + 1, NImages):
    HistName = "LightsOffFiles_" + str(i) + "-" + str(j)
    HistTitl = "Subtraction histogram for LightsOffFiles " + str(i) + " - " + str(j)
    LightsOffSubtrImages.append(ROOT.TH2D(HistName, HistTitl, NBinsX, XLo, XHi, NBinsY, YLo, YHi))
    LightsOffSubtrImages[-1].GetXaxis().SetTitle(XTitle)
    LightsOffSubtrImages[-1].GetXaxis().SetTitleOffset(XTOfst)
    LightsOffSubtrImages[-1].GetYaxis().SetTitle(YTitle)
    LightsOffSubtrImages[-1].GetYaxis().SetTitleOffset(YTOfst)
    LightsOffSubtrImages[-1].Add(LightsOffImages[i],  1.)
    LightsOffSubtrImages[-1].Add(LightsOffImages[j], -1.)
    LightsOffSubtrImages[-1].GetZaxis().SetRangeUser(-1. * PixelValueHalfRange, PixelValueHalfRange)
    LightsOffSubtrImages[-1].Draw("colz")
    aCanvas.Update()
    aCanvas.SaveAs(OutputFileDirectory + HistName + ".png")

# Get the mean and RMS of each of the subtraction histograms.
MarkerSize = 3
Zeros = range(len(LightsOnSubtrImages))
for i in range(len(Zeros)):
  Zeros[i] = 0.
ImageNumber = range(len(LightsOnSubtrImages))
# Lights on, cover off....
LightsOnAvg = []
LightsOnRMS = []
for histo in LightsOnSubtrImages: 
  thisAvg, thisRMS = PrintMeanAndRMSofImage(histo)
  LightsOnAvg.append(thisAvg)
  LightsOnRMS.append(thisRMS)
LightsOnGraph = PythonTools.CreateTGraph(array.array("f", ImageNumber), array.array("f", LightsOnAvg),
                                         array.array("f", Zeros),       array.array("f", LightsOnRMS),
                                         "LightsOnGraph", "Mean and RMS for Lights On, Cover Off Subtraction Images", 
                                         ROOT.kBlack, "Subtraction Image Number", "Average Pixel Value [ADC Units]")
LightsOnGraph.SetMarkerStyle(20)
LightsOnGraph.SetMarkerSize(MarkerSize)

# Lights on, cover on....
CoverOnAvg = []
CoverOnRMS = []
for histo in CoverOnSubtrImages : 
  thisAvg, thisRMS = PrintMeanAndRMSofImage(histo)
  CoverOnAvg.append(thisAvg)
  CoverOnRMS.append(thisRMS)
CoverOnGraph = PythonTools.CreateTGraph(array.array("f", ImageNumber), array.array("f", CoverOnAvg),
                                        array.array("f", Zeros),       array.array("f", CoverOnRMS),
                                        "CoverOnGraph", "Mean and RMS for Lights On, Cover On Subtraction Images", 
                                        ROOT.kBlue, "Subtraction Image Number", "Average Pixel Value [ADC Units]")
CoverOnGraph.SetMarkerStyle(21)
CoverOnGraph.SetMarkerSize(MarkerSize)
# Lights off, cover on....
LightsOffCoverOnAvg = []
LightsOffCoverOnRMS = []
for histo in LightsOffCoverOnSubtrImages: 
  thisAvg, thisRMS = PrintMeanAndRMSofImage(histo)
  LightsOffCoverOnAvg.append(thisAvg)
  LightsOffCoverOnRMS.append(thisRMS)
LightsOffCoverOnGraph = PythonTools.CreateTGraph(array.array("f", ImageNumber), array.array("f", LightsOffCoverOnAvg),
                                                 array.array("f", Zeros),       array.array("f", LightsOffCoverOnRMS),
                                                 "LightsOffCoverOnGraph", "Mean and RMS for Lights Off, Cover On Subtraction Images", 
                                                 ROOT.kGreen - 1, "Subtraction Image Number", "Average Pixel Value [ADC Units]")
LightsOffCoverOnGraph.SetMarkerStyle(22)
LightsOffCoverOnGraph.SetMarkerSize(MarkerSize)
# Lights off, cover off....
LightsOffAvg = []
LightsOffRMS = []
for histo in LightsOffSubtrImages: 
  thisAvg, thisRMS = PrintMeanAndRMSofImage(histo)
  LightsOffAvg.append(thisAvg)
  LightsOffRMS.append(thisRMS)
LightsOffGraph = PythonTools.CreateTGraph(array.array("f", ImageNumber), array.array("f", LightsOffAvg),
                                          array.array("f", Zeros),       array.array("f", LightsOffRMS),
                                          "LightsOffGraph", "Mean and RMS for Lights Off, Cover Off Subtraction Images", 
                                          ROOT.kRed, "Subtraction Image Number", "Average Pixel Value [ADC Units]")
LightsOffGraph.SetMarkerStyle(23)
LightsOffGraph.SetMarkerSize(MarkerSize)

# Plot all these average value graphs together:
ROOT.gStyle.SetOptTitle(0)
aPad.SetLeftMargin(0.06)
aPad.SetRightMargin(0.02)
aPad.SetTopMargin(0.02)
CanvasSetupHisto = ROOT.TH2D("CanvasSetupHisto", "Plots, plots, plots...", 
                             1, -0.5, float(len(ImageNumber)) - 0.5, 1, -700., 700.)
CanvasSetupHisto.GetXaxis().SetTitle("Subtraction Image Number")
CanvasSetupHisto.GetYaxis().SetTitle("Average Pixel Value [ADC Units]")
CanvasSetupHisto.GetYaxis().SetTitleOffset(0.8)
CanvasSetupHisto.Draw()
for plot in [LightsOnGraph, CoverOnGraph, LightsOffCoverOnGraph, LightsOffGraph]:
  plot.Draw("p")
GraphLegend = ROOT.TLegend(0.09,0.115, 0.45,0.30)
GraphLegend.SetFillColor(ROOT.kWhite)
GraphLegend.SetTextFont(42)
GraphLegend.SetNColumns(2)
GraphLegend.AddEntry(LightsOnGraph,         "Lights on, Cover off",  "p")
GraphLegend.AddEntry(CoverOnGraph,          "Lights on, Cover on",   "p")
GraphLegend.AddEntry(LightsOffCoverOnGraph, "Lights off, Cover on",  "p")
GraphLegend.AddEntry(LightsOffGraph,        "Lights off, Cover off", "p")
GraphLegend.Draw()
aCanvas.Update()
aCanvas.SaveAs("./SubtractionImageMeanGraph.pdf")


# Now, create a pixel value histogram for each of the image histograms, and fit out the mean and width.
# Lights on...
aPad.SetTopMargin(0.08)
LightsOnPVHistos = []
for imagehisto in LightsOnImages:
  LightsOnPVHistos.append(MakePVHisto(imagehisto))
GausFitModel = PythonTools.GetOneGausFitModel("GausFitModel", LightsOnPVHistos[0], 0., 50.)
for histo in LightsOnPVHistos:
  DoDarkNoiseAnalysis(histo, GausFitModel)
# Cover on...
CoverOnPVHistos = []
for imagehisto in CoverOnImages:
  CoverOnPVHistos.append(MakePVHisto(imagehisto))
GausFitModel = PythonTools.GetOneGausFitModel("GausFitModel", CoverOnPVHistos[0], 0., 50.)
for histo in CoverOnPVHistos:
  DoDarkNoiseAnalysis(histo, GausFitModel)
# Lights off, cover on...
LightsOffCoverOnPVHistos = []
for imagehisto in LightsOffCoverOnImages:
  LightsOffCoverOnPVHistos.append(MakePVHisto(imagehisto))
GausFitModel = PythonTools.GetOneGausFitModel("GausFitModel", LightsOffCoverOnPVHistos[0], 0., 50.)
for histo in LightsOffCoverOnPVHistos:
  DoDarkNoiseAnalysis(histo, GausFitModel)
# Lights off, cover off...
LightsOffPVHistos = []
for imagehisto in LightsOffImages:
  LightsOffPVHistos.append(MakePVHisto(imagehisto))
GausFitModel = PythonTools.GetOneGausFitModel("GausFitModel", LightsOffPVHistos[0], 0., 50.)
for histo in LightsOffPVHistos:
  DoDarkNoiseAnalysis(histo, GausFitModel)

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
