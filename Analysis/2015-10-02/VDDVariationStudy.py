#!/usr/bin/python

####################################################################################################
# In early October, Sufia and I looked at varying the VDD/Output voltage for the SpectroCCD to     #
# look at its effect on the x ray collection and noise as a function of this parameter.  There is  #
# an x ray exposure and a dark image for each one.  We've already descrambled and flattened the    #
# images and converted them to TH2D objects.  Now we'll open up each x ray and dark frame,         #
# the latter from the former, and then make the Sum(N) spectra from each one.                      #
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

def MakeTH2DForDarkSubtraction(name, title, templatehisto):
  NewHisto = ROOT.TH2D(name, title,
                       templatehisto.GetXaxis().GetNbins(), templatehisto.GetXaxis().GetXmin(), templatehisto.GetXaxis().GetXmax(),
                       templatehisto.GetYaxis().GetNbins(), templatehisto.GetYaxis().GetXmin(), templatehisto.GetYaxis().GetXmax())
  NewHisto.GetXaxis().SetTitle(templatehisto.GetXaxis().GetTitle())
  NewHisto.GetYaxis().SetTitle(templatehisto.GetYaxis().GetTitle())
  NewHisto.GetXaxis().SetTitleOffset(templatehisto.GetXaxis().GetTitleOffset())
  NewHisto.GetYaxis().SetTitleOffset(templatehisto.GetYaxis().GetTitleOffset())
  return NewHisto



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
PlotImageHisto =  False

# Pull in the path to the root files we're going to look at:
InputFilePath_VDD1816_Dark = "/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-02_xray/dark5s_VDD14_18V_VDD23_16V/dark5s_VDD14_18V_VDD23_16V_UnShuf.root"
InputFilePath_VDD1816_XRay = "/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-02_xray/xray5s_VDD14_18V_VDD23_16V/xray5s_VDD14_18V_VDD23_16V_UnShuf.root"
InputFilePath_VDD2018_Dark = "/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-02_xray/dark5s_VDD14_20V_VDD23_18V/dark5s_VDD14_20V_VDD23_18V_UnShuf.root"
InputFilePath_VDD2018_XRay = "/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-02_xray/xray5s_VDD14_20V_VDD23_18V/xray5s_VDD14_20V_VDD23_18V_UnShuf.root"
InputFilePath_VDD2220_Dark = "/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-02_xray/dark5s_VDD14_22V_VDD23_20V/dark5s_VDD14_22V_VDD23_20V_UnShuf.root"
InputFilePath_VDD2220_XRay = "/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-02_xray/xray5s_VDD14_22V_VDD23_20V/xray5s_VDD14_22V_VDD23_20V_UnShuf.root"
InputFilePath_VDD2422_Dark = "/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-02_xray/dark5s_VDD14_24V_VDD23_22V/dark5s_VDD14_24V_VDD23_22V_UnShuf.root"
InputFilePath_VDD2422_XRay = "/Users/vmgehman/Documents/Detectorstan/SpectroCCD/Images/2015-10-02_xray/xray5s_VDD14_24V_VDD23_22V/xray5s_VDD14_24V_VDD23_22V_UnShuf.root"

# Crack open the files, get the 2D image histograms...
InputFile_VDD1816_Dark = ROOT.TFile(InputFilePath_VDD1816_Dark)
InputFile_VDD1816_XRay = ROOT.TFile(InputFilePath_VDD1816_XRay)
InputFile_VDD2018_Dark = ROOT.TFile(InputFilePath_VDD2018_Dark)
InputFile_VDD2018_XRay = ROOT.TFile(InputFilePath_VDD2018_XRay)
InputFile_VDD2220_Dark = ROOT.TFile(InputFilePath_VDD2220_Dark)
InputFile_VDD2220_XRay = ROOT.TFile(InputFilePath_VDD2220_XRay)
InputFile_VDD2422_Dark = ROOT.TFile(InputFilePath_VDD2422_Dark)
InputFile_VDD2422_XRay = ROOT.TFile(InputFilePath_VDD2422_XRay)
ImageHisto_VDD1816_Dark = InputFile_VDD1816_Dark.Get("thatHistogram")
ImageHisto_VDD1816_XRay = InputFile_VDD1816_XRay.Get("thatHistogram")
ImageHisto_VDD2018_Dark = InputFile_VDD2018_Dark.Get("thatHistogram")
ImageHisto_VDD2018_XRay = InputFile_VDD2018_XRay.Get("thatHistogram")
ImageHisto_VDD2220_Dark = InputFile_VDD2220_Dark.Get("thatHistogram")
ImageHisto_VDD2220_XRay = InputFile_VDD2220_XRay.Get("thatHistogram")
ImageHisto_VDD2422_Dark = InputFile_VDD2422_Dark.Get("thatHistogram")
ImageHisto_VDD2422_XRay = InputFile_VDD2422_XRay.Get("thatHistogram")

# Now build up the dark-subtracted image histograms.
ImageHisto_VDD1816 = MakeTH2DForDarkSubtraction("ImageHisto_VDD1816", 
                                                "Dark Subtracted Image for VDD_{1,4} = 18V and VDD_{2,3} = 16V", 
                                                ImageHisto_VDD1816_XRay)
ImageHisto_VDD2018 = MakeTH2DForDarkSubtraction("ImageHisto_VDD2018", 
                                                "Dark Subtracted Image for VDD_{1,4} = 20V and VDD_{2,3} = 18V", 
                                                ImageHisto_VDD2018_XRay)
ImageHisto_VDD2220 = MakeTH2DForDarkSubtraction("ImageHisto_VDD2220", 
                                                "Dark Subtracted Image for VDD_{1,4} = 22V and VDD_{2,3} = 20V", 
                                                ImageHisto_VDD2220_XRay)
ImageHisto_VDD2422 = MakeTH2DForDarkSubtraction("ImageHisto_VDD2422", 
                                                "Dark Subtracted Image for VDD_{1,4} = 24V and VDD_{2,3} = 22V", 
                                                ImageHisto_VDD2422_XRay)

# Take our new histograms and add the x ray exposure and subtract the dark.
ImageHisto_VDD1816.Add(ImageHisto_VDD1816_XRay,  1.)
ImageHisto_VDD1816.Add(ImageHisto_VDD1816_Dark, -1.)
ImageHisto_VDD2018.Add(ImageHisto_VDD2018_XRay,  1.)
ImageHisto_VDD2018.Add(ImageHisto_VDD2018_Dark, -1.)
ImageHisto_VDD2220.Add(ImageHisto_VDD2220_XRay,  1.)
ImageHisto_VDD2220.Add(ImageHisto_VDD2220_Dark, -1.)
ImageHisto_VDD2422.Add(ImageHisto_VDD2422_XRay,  1.)
ImageHisto_VDD2422.Add(ImageHisto_VDD2422_Dark, -1.)
ImageHistos = [ImageHisto_VDD1816, ImageHisto_VDD2018, ImageHisto_VDD2220, ImageHisto_VDD2422]

# Set up the range over which we are going to do the analysis.
xLo =  0.5
xHi = 12.
yLo =  1.
yHi = 27.

# If the flag is set, go ahead and plot this thing now...
if(PlotImageHisto):
  aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
  aCanvas.Draw()
  aCanvas.cd()
  aPad.SetLeftMargin(0.05)
  aPad.SetRightMargin(0.12)
  aPad.SetBottomMargin(0.08)
  aPad.SetLogy(0)
  aPad.Draw()
  aPad.cd()
  for ImageHisto in ImageHistos:
    ImageHisto.GetXaxis().SetRangeUser(xLo, xHi)
    ImageHisto.GetYaxis().SetRangeUser(yLo, yHi)
    ImageHisto.Draw("colz")
    aCanvas.Update()
    aCanvas.SaveAs("./" + ImageHisto.GetName() + ".png")
    aCanvas.Clear()
  del aPad
  del aCanvas

# Now, we need to loop over all the bins in the TH2D and pick out the x ray hit clusters.  Since
# the pixels are nine times bigger in the y direction than in the y direction, charge is more
# likely to be shared between neighboring pixels in the x direction.  That means that we're going
# to step over *rows* pixels in the x direction for each y position, and find local maxima.  Since
# the images are all the same size, we only have to do this once.
xBinsToAnalyze = range(ImageHistos[0].GetXaxis().FindBin(xLo), ImageHistos[0].GetXaxis().FindBin(xHi) + 1)
yBinsToAnalyze = range(ImageHistos[0].GetYaxis().FindBin(yLo), ImageHistos[0].GetYaxis().FindBin(yHi) + 1)
if(Debugging):
  print xBinsToAnalyze
  print yBinsToAnalyze
iYBin = 0
yPixelSize = 45. / 1000. #[mm]

# Loop over the dark subtracted images...
for ImageHisto in ImageHistos:
  # We would like to track the average and RMS of the pixelvalues in each row.
  RowAvgData = []
  RowRMSData = []
  YPosition = []
  YPositiEr = []
  # We would also like to track the number of pixels that above threshold (some number of RMS), and
  # therefore are candidate x ray interaction sites in each row of pixels.
  ThresholdInRMS = 10.
  ThresholdData = []
  ThresholdDepartureData = []
  # And here is where we will store all the bins above threshold and their values.
  xBinsAboveThreshold = []
  yBinsAboveThreshold = []
  PixelValuesAboveThr = []
  # Since we're going to end up making a bunch of pixel value histograms, we're going to want to
  # keep track of the range over which pixel values vary.
  MaxPixVal = -1.e6
  MinPixVal =  1.e6
  # Loop over the bins in the y direction...
  for yBin in yBinsToAnalyze:
    if((len(yBinsToAnalyze) >= 100) and (iYBin % int(len(yBinsToAnalyze) / 100) == 0)):
      ROOT.StatusBar(iYBin, len(yBinsToAnalyze), len(yBinsToAnalyze) / 100)
    RowAvg   = 0.
    RowSqAvg = 0.
    # Loop over the pixels in the x direction at this value of y...
    for xBin in xBinsToAnalyze:
      thisPixVal = ImageHisto.GetBinContent(xBin, yBin)
      if(thisPixVal > MaxPixVal): MaxPixVal = thisPixVal
      if(thisPixVal < MinPixVal): MinPixVal = thisPixVal
      RowAvg   += ImageHisto.GetBinContent(xBin, yBin) / (len(xBinsToAnalyze) * len(yBinsToAnalyze))
      RowSqAvg += (ImageHisto.GetBinContent(xBin, yBin)**2.) / (len(xBinsToAnalyze) * len(yBinsToAnalyze))
    iYBin += 1
    RowRMS = RowSqAvg - (RowAvg**2.)
    YPosition.append(float(yBin) * yPixelSize)
    YPositiEr.append(0.)
    RowAvgData.append(RowAvg)
    RowRMSData.append(RowRMS)
    ThresholdData.append(ThresholdInRMS * RowRMS)
    # Now that we know the mean and RMS, loop back over this row, count the number of departures
    # above threshold, and track which bins do so.
    nDepartures = 0
    for xBin in xBinsToAnalyze:
      thisBinVal = ImageHisto.GetBinContent(xBin, yBin)
      if(thisBinVal > (ThresholdInRMS * RowRMS)):
        nDepartures += 1
        xBinsAboveThreshold.append(xBin)
        yBinsAboveThreshold.append(yBin)
        PixelValuesAboveThr.append(thisBinVal)
        #print "Pixel:", xBin, yBin, "with value", thisBinVal, "greater than", ThresholdInRMS * RowRMS
    ThresholdDepartureData.append(nDepartures)
  print 
  if(VerboseProcessing): 
    print "\tTotal range of pixel values went from", MinPixVal, "to", MaxPixVal
    print "\tAverage pixel value:", numpy.mean(RowAvgData), "+/-", numpy.mean(RowRMSData)
    print "\tTotal of", len(PixelValuesAboveThr), "pixels were above threshold."
  # Make a nice TGraph of the average image value as a function of y position.
  yPositionPlotPad = 0.5
  YPosition = array.array("f", YPosition)
  YPositiEr = array.array("f", YPositiEr)
  RowAvgData = array.array("f", RowAvgData)
  RowRMSData = array.array("f", RowRMSData)
  RowAvgGraph = PythonTools.CreateTGraph(YPosition, RowAvgData, YPositiEr, RowRMSData, "RowAvgGraph", "Pixel Row Average", ROOT.kBlack, "Y Position [mm]", "Average Pixel Value [ADC]")
  RowAvgGraph.GetXaxis().SetRangeUser(yLo - yPositionPlotPad, yHi + yPositionPlotPad)
  aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
  aCanvas.Draw()
  aCanvas.cd()
  aPad.SetLeftMargin(0.08)
  aPad.SetRightMargin(0.015)
  aPad.SetBottomMargin(0.09)
  aPad.SetLogy(0)
  aPad.Draw()
  aPad.cd()
  RowAvgGraph.Draw("ap")
  aCanvas.Update()
  aCanvas.SaveAs("./" + ImageHisto.GetName() + ".PixRowAvg.pdf")
  # Now plot the number of threshold departures as a function of y position.
  ThresholdDepartureData = array.array("f", ThresholdDepartureData)
  ThresholdDepartureGraph = PythonTools.CreateTGraph(YPosition, ThresholdDepartureData, YPositiEr, YPositiEr, "ThresholdDepartureGraph", "Number of Threshold Departures", ROOT.kBlack, "Y Position [mm]", "Number of Threshold Departures")
  ThresholdDepartureGraph.GetXaxis().SetRangeUser(yLo - yPositionPlotPad, yHi + yPositionPlotPad)
  ThresholdDepartureGraph.GetYaxis().SetRangeUser(0., 1.1 * max(ThresholdDepartureData))
  ThresholdDepartureGraph.Draw("ap")
  aCanvas.Update()
  aCanvas.SaveAs("./" + ImageHisto.GetName() + ".nThresDep.pdf")
  # Now plot the threshold in ADC Units as a function of y position.
  ThresholdData = array.array("f", ThresholdData)
  ThresholdGraph = PythonTools.CreateTGraph(YPosition, ThresholdData, YPositiEr, YPositiEr, "ThresholdGraph", "Threshold Values", ROOT.kBlack, "Y Position [mm]", "Threshold Value [ADC]")
  ThresholdGraph.GetXaxis().SetRangeUser(yLo - yPositionPlotPad, yHi + yPositionPlotPad)
  ThresholdGraph.GetYaxis().SetRangeUser(0., 1.1 * max(ThresholdData))
  ThresholdGraph.Draw("ap")
  aCanvas.Update()
  aCanvas.SaveAs("./" + ImageHisto.GetName() + ".ThreshVals.pdf")
  #exit()
  # Now, let's make a series of pixel value histograms and fill them appropriately.
  PixValLo = round(MinPixVal, -3)
  if(PixValLo > -1000.): PixValLo = -1000.
  PixValHi = round(MaxPixVal, -3)
  if(PixValHi <  1000.): PixValHi = 1000.
  PixValBW = 10.
  nPixValBins = 0
  thisBinVal = PixValLo
  while(thisBinVal <= PixValHi):
    nPixValBins += 1
    thisBinVal = PixValLo + (float(nPixValBins) * PixValBW)
  print "\tHistogramming ALL pixel values..."
  PixValHisto_All = PythonTools.MakePixValHisto("PixValHisto_All", "Histogram of All Pixel Values", nPixValBins, PixValLo, PixValHi, ROOT.kBlack)
  iYBin = 0
  for yBin in yBinsToAnalyze:
    if((len(yBinsToAnalyze) >= 100) and (iYBin % int(len(yBinsToAnalyze) / 100) == 0)):
      ROOT.StatusBar(iYBin, len(yBinsToAnalyze), len(yBinsToAnalyze) / 100)
    for xBin in xBinsToAnalyze:
      PixValHisto_All.Fill(ImageHisto.GetBinContent(xBin, yBin))
    iYBin += 1
  print
  aPad.SetRightMargin(0.025)
  aPad.SetLogy(1)
  PixValHisto_All.Draw()
  PixValHisto_All.GetXaxis().SetRangeUser(-800., 1200)
  PixValHisto_All.GetYaxis().SetRangeUser(0.5, 1.1 * PixValHisto_All.GetMaximum())
  # Fit a Gaussian to the pedestal region of the histogram of all pixel values to get the with of
  # the noise peak.
  FitModel_All = PythonTools.GetOneGausFitModel("FitModel_All", PixValHisto_All, 0.,  80.)
  PixValHisto_All.Fit(FitModel_All, "LLEM", "", -200., 200.)
  FitComponents_All = PythonTools.GetOneGausFitComponents(FitModel_All)
  for fitcomp in FitComponents_All:
    fitcomp.Draw("same")
  aCanvas.Update()
  FitAnnotation_All = PythonTools.MakeOneGausFitAnnotation(FitModel_All)
  FitAnnotation_All.Draw()
  aCanvas.Update()
  aCanvas.SaveAs("./" + ImageHisto.GetName() + "." + PixValHisto_All.GetName() + ".pdf")
  # Set the title of this histogram to something that will fit in the legend of the composit plot
  # we're going to make at the end...
  PixValHisto_All.SetTitle("All")
  #exit()
  print "\tHistogramming pixel values above threshold..."
  PixValHisto_AbvThrsh = PythonTools.MakePixValHisto("PixValHisto_AbvThrsh", "Histogram of Pixels Passing Threhsold Cut", nPixValBins, PixValLo, PixValHi, ROOT.kBlack)
  ipv = 0
  for pixval in PixelValuesAboveThr:
    if((len(PixelValuesAboveThr) >= 100) and (ipv % int(len(PixelValuesAboveThr) / 100) == 0)):
      ROOT.StatusBar(ipv, len(PixelValuesAboveThr), len(PixelValuesAboveThr) / 100)
    PixValHisto_AbvThrsh.Fill(pixval)
    #print "Pixel:", xBinsAboveThreshold[ipv], yBinsAboveThreshold[ipv], "with value", pixval, "or", PixelValuesAboveThr[ipv], "or better yet", ImageHisto.GetBinContent(xBinsAboveThreshold[ipv], yBinsAboveThreshold[ipv])
    ipv += 1
  print
  aPad.SetLogy(1)
  PixValHisto_AbvThrsh.Draw()
  PixValHisto_AbvThrsh.GetXaxis().SetRangeUser(-100., 1500.)
  PixValHisto_AbvThrsh.GetYaxis().SetRangeUser(0.5, 5.e4)
  FitModel_AbvThrsh = PythonTools.GetRWFitModel("FitModel_AbvThrsh", PixValHisto_AbvThrsh, 400., 375.)
  PixValHisto_AbvThrsh.Fit(FitModel_AbvThrsh, "LLEM", "", 400., 3000.)
  #FitComponents_AbvThrsh = PythonTools.GetTwoGausFitComponents(FitModel_AbvThrsh)
  FitComponents_AbvThrsh = PythonTools.GetRWFitModelComponents(FitModel_AbvThrsh)
  for fitcomp in FitComponents_AbvThrsh:
    fitcomp.Draw("same")
  aCanvas.Update()
  FitAnnotation_AbvThrsh = PythonTools.MakeFitAnnotationRW(FitModel_AbvThrsh)
  FitAnnotation_AbvThrsh.Draw()
  aCanvas.Update()
  aCanvas.SaveAs("./" + ImageHisto.GetName() + "." + PixValHisto_AbvThrsh.GetName() + ".pdf")
  PixValHisto_AbvThrsh.SetTitle("Thresh. Cut")
  print "\tFinding aixels above threshold that are local maxima..."
  xBinsLocMax = []
  yBinsLocMax = []
  for i in range(len(PixelValuesAboveThr)):
    if((len(PixelValuesAboveThr) >= 100) and (i % int(len(PixelValuesAboveThr) / 100) == 0)):
      ROOT.StatusBar(i, len(PixelValuesAboveThr), len(PixelValuesAboveThr) / 100)
    LocalMax = True
    thisPixVal = PixelValuesAboveThr[i]
    thisPixVal_1up = ImageHisto.GetBinContent(xBinsAboveThreshold[i],     yBinsAboveThreshold[i] + 1)
    thisPixVal_1dn = ImageHisto.GetBinContent(xBinsAboveThreshold[i],     yBinsAboveThreshold[i] - 1)
    thisPixVal_1lf = ImageHisto.GetBinContent(xBinsAboveThreshold[i] - 1, yBinsAboveThreshold[i])
    thisPixVal_1rt = ImageHisto.GetBinContent(xBinsAboveThreshold[i] + 1, yBinsAboveThreshold[i])
    thisPixVal_2lf = ImageHisto.GetBinContent(xBinsAboveThreshold[i] - 2, yBinsAboveThreshold[i])
    thisPixVal_2rt = ImageHisto.GetBinContent(xBinsAboveThreshold[i] + 2, yBinsAboveThreshold[i])
    thisPixVal_3lf = ImageHisto.GetBinContent(xBinsAboveThreshold[i] - 3, yBinsAboveThreshold[i])
    thisPixVal_3rt = ImageHisto.GetBinContent(xBinsAboveThreshold[i] + 3, yBinsAboveThreshold[i])
    NeighboringPixVals = [thisPixVal_1up, thisPixVal_1dn, thisPixVal_1lf, thisPixVal_1rt, thisPixVal_2lf, thisPixVal_2rt, thisPixVal_3lf, thisPixVal_3rt]
    for npv in NeighboringPixVals:
      if(thisPixVal < npv): LocalMax = False
    if(LocalMax):
      xBinsLocMax.append(xBinsAboveThreshold[i])
      yBinsLocMax.append(yBinsAboveThreshold[i])
  print
  print "\tPopulating Sum(1, 3, 5, 7, 9) histograms..."
  PixValHisto_Sum1 = PythonTools.MakePixValHisto("PixValHisto_Sum1", "Sum(1) Histogram", nPixValBins, PixValLo, PixValHi, ROOT.kGreen)
  PixValHisto_Sum3 = PythonTools.MakePixValHisto("PixValHisto_Sum3", "Sum(3) Histogram", nPixValBins, PixValLo, PixValHi, ROOT.kCyan)
  PixValHisto_Sum5 = PythonTools.MakePixValHisto("PixValHisto_Sum5", "Sum(5) Histogram", nPixValBins, PixValLo, PixValHi, ROOT.kOrange)
  PixValHisto_Sum7 = PythonTools.MakePixValHisto("PixValHisto_Sum7", "Sum(7) Histogram", nPixValBins, PixValLo, PixValHi, ROOT.kViolet)
  PixValHisto_Sum9 = PythonTools.MakePixValHisto("PixValHisto_Sum9", "Sum(9) Histogram", nPixValBins, PixValLo, PixValHi, ROOT.kTeal)
  for i in range(len(xBinsLocMax)):
    if((len(xBinsLocMax) >= 100) and (i % int(len(xBinsLocMax) / 100) == 0)):
      ROOT.StatusBar(i, len(xBinsLocMax), len(xBinsLocMax) / 100)
    # Construct all the Sum(N) values...
    Sum1Val = ImageHisto.GetBinContent(xBinsLocMax[i], yBinsLocMax[i])
    Sum3Val = 0.
    for j in range(-1, 2):
      thisPixVal = ImageHisto.GetBinContent(xBinsLocMax[i] + j, yBinsLocMax[i])
      Sum3Val += thisPixVal
    Sum5Val = 0.
    for j in range(-2, 3):
      thisPixVal = ImageHisto.GetBinContent(xBinsLocMax[i] + j, yBinsLocMax[i])
      Sum5Val += thisPixVal
    Sum7Val = 0.
    for j in range(-3, 4):
      thisPixVal = ImageHisto.GetBinContent(xBinsLocMax[i] + j, yBinsLocMax[i])
      Sum7Val += thisPixVal
    Sum9Val = 0.
    for j in range(-4, 5):
      thisPixVal = ImageHisto.GetBinContent(xBinsLocMax[i] + j, yBinsLocMax[i])
      Sum9Val += thisPixVal
    # Now populate the Sum(N) histograms...
    PixValHisto_Sum1.Fill(Sum1Val)
    PixValHisto_Sum3.Fill(Sum3Val)
    PixValHisto_Sum5.Fill(Sum5Val)
    PixValHisto_Sum7.Fill(Sum7Val)
    PixValHisto_Sum9.Fill(Sum9Val)
  print 
  FitModels_SumN = []
  SumHists = [PixValHisto_Sum1, PixValHisto_Sum3, PixValHisto_Sum5, PixValHisto_Sum7, PixValHisto_Sum9]
  ShrtName = ["Sum(1)",      "Sum(3)",          "Sum(5)",         "Sum(7)",         "Sum(9)"]
  Means    = [ 600.,             850.,             1500.,            1850.,            1900.]
  Sigmas   = [ 200.,             300.,              300.,             450.,             450.]
  FitLos   = [ 400.,             600.,             1000.,            1200.,            1300.]
  FitHis   = [2000.,            2500.,             3000.,            3500.,            3500.]
  for i in range(len(SumHists)):
    SumHists[i].GetXaxis().SetRangeUser(-100., 5000.)
    SumHists[i].GetYaxis().SetRangeUser(0.5, 5.e4)
    SumHists[i].Draw()
    aCanvas.Update()
    FitModels_SumN.append(PythonTools.GetRWFitModel("FitModel_" + SumHists[i].GetName(), SumHists[i], Means[i], Sigmas[i]))
    SumHists[i].Fit(FitModels_SumN[i], "LLEM", "", FitLos[i], FitHis[i])
    FitComponents_SumN = PythonTools.GetRWFitModelComponents(FitModels_SumN[i])
    for fitcomp in FitComponents_SumN:
      fitcomp.Draw("same")
    aCanvas.Update()
    FitAnnotation = PythonTools.MakeFitAnnotationRW(FitModels_SumN[i])
    FitAnnotation.Draw()
    aCanvas.SaveAs("./" + ImageHisto.GetName() + "." + SumHists[i].GetName() + ".pdf")
    SumHists[i].SetTitle(ShrtName[i])
  # Just for fun, let's make a group shot of all the pixel value histograms...
  ROOT.gStyle.SetOptTitle(0)
  aPad.SetTopMargin(0.01)
  aPad.SetLogy(1)
  PixValHisto_All.GetXaxis().SetRangeUser(-800., 3500.)
  PixValHisto_All.GetYaxis().SetRangeUser(0.2, 2000.)
  PixValHisto_All.Fit("gaus", "Q0")
  PixValHisto_All.Draw()
  aCanvas.Update()
  OtherPixValHists = [PixValHisto_Sum1, PixValHisto_Sum3, PixValHisto_Sum5, PixValHisto_Sum7, PixValHisto_Sum9]
  for pixvalhist in OtherPixValHists:
    pixvalhist.Fit("gaus", "Q0")
    pixvalhist.Draw("same")
    aCanvas.Update()
  aLegend = ROOT.TLegend(0.60,0.78, 0.97,0.98)
  aLegend.SetFillColor(ROOT.kWhite)
  aLegend.SetTextFont(ROOT.gStyle.GetTextFont())
  aLegend.SetNColumns(3)
  aLegend.AddEntry(PixValHisto_All, PixValHisto_All.GetTitle(), "l")
  for pixvalhist in OtherPixValHists:
    aLegend.AddEntry(pixvalhist, pixvalhist.GetTitle(), "l")
  aLegend.Draw()
  aCanvas.Update()
  aCanvas.SaveAs("./" + ImageHisto.GetName() + ".AllPixValHistos.pdf")
  # Save the Sum(N) spectra to a root file so that we can do stuff with them later.
  OutputFile = ROOT.TFile("./" + ImageHisto.GetName() + ".xrayAnalysis.root", "recreate")
  for plot in OtherPixValHists:
    plot.Write()
  OutputFile.Close()

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
