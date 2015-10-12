#!/usr/bin/python

###################################################################################################
# Support functions for fits file analysis.                                                       #
###################################################################################################

import ROOT
import array
import numpy

# Correct for the row and column offsets...
def FixSpectroCCDOffset(row, column, nrows, ncolumns, rowoffset, columnoffset):
  NewRow = row - rowoffset
  if(NewRow < 0): NewRow += nrows
  NewColumn = column - columnoffset
  if(NewColumn < 0): NewColumn += ncolumns
  return NewRow, NewColumn

# Asign a new row and column to an input pixel that removes the overscan region that shows up in
# as vertical and horizontal bands in the middle of the image.  
def RemoveSpectroCCDOverscan(row, column, npixelsyold, npixelsxold, nrealpixelsy, nrealpixelsx):
  OverscanRowStart = nrealpixelsy
  OverscanRowStop  = npixelsyold - (nrealpixelsy)
  OverscanColStart = nrealpixelsx / 4
  OverscanColStop  = npixelsxold - (nrealpixelsx / 4)
  #print "Overscan rows go from", OverscanRowStart, "to", OverscanRowStop
  #print "Overscan cols go from", OverscanColStart, "to", OverscanColStop
  NewRow    = -10 # Initialize these two to the overscan region, and then move them out if it
  NewColumn = -10 # makes sense to do so.
  if(row < OverscanRowStart): NewRow = row
  if(row >= OverscanRowStop): NewRow = row - (npixelsyold - (2 * nrealpixelsy))
  if(column < OverscanColStart): NewColumn = column
  if(column >= OverscanColStop): NewColumn = column - (npixelsxold - (nrealpixelsx / 2))
  return NewRow, NewColumn

# Return the quadrant of the CCD readout.  It's defined just like the x-y plane:
# 2 | 1
# -----
# 3 | 4
def GetSpectroCCDQuadrant(row, column, nrows, ncolumns):
  Quadrant = 0
  if((row <  (nrows / 2)) and (column >= (ncolumns / 2))): Quadrant = 1
  if((row <  (nrows / 2)) and (column <  (ncolumns / 2))): Quadrant = 2
  if((row >= (nrows / 2)) and (column <  (ncolumns / 2))): Quadrant = 3
  if((row >= (nrows / 2)) and (column >= (ncolumns / 2))): Quadrant = 4
  if(Quadrant == 0): 
    print "\tWhat happened in row", row, "and column", str(column) + "?  It seems to still be a", Quadrant
  return Quadrant

def FlipSpectroCCDBottom(row, column, nrows, ncolumns):
  # Decide which quadrant of the old image we're in.
  Quadrant = GetSpectroCCDQuadrant(row, column, nrows, ncolumns)
  NewRow = -1
  NewColumn = -1
  # If we're in quadrant 1 or 2, do nothing:
  if((Quadrant == 1) or (Quadrant == 2)):
    NewRow = row
    NewColumn = column
  # If we're in quadrant 3 or 4, reflect about the middle of the chip.
  if((Quadrant == 3) or (Quadrant == 4)):
    NewRow = row
    NewColumn = ncolumns - 1 - column
  if(NewRow >= nrows):
    print "\tError in bottom flip: row", row, "maps to", NewRow, "which is greater than", nrows
  if(NewRow < 0):
    print "\tError in bottom flip: row", row, "maps to", NewRow, "which is less than", 0
  if(NewColumn >= ncolumns):
    print "\tError in bottom flip: column", column, "maps to", NewColumn, "which is greater than", ncolumns
  if(NewColumn < 0):
    print "\tError in bottom flip: column", column, "maps to", NewColumn, "which is less than", 0
  return NewRow, NewColumn

# Interdigitate the quadrants of the image that comes out of the CCD controler to reconstruct the actual image.
def InterdigitateSpectroCCDPixels(row, column, nrowsold, ncolumnsold, nrowsnew, ncolumnsnew):
  # Decide which quadrant of the old image we're in.
  Quadrant = GetSpectroCCDQuadrant(row, column, nrowsold, ncolumnsold)
  NewRow = -1
  NewColumn = -1
  # Based on that, shuffle the columns of the image together.
  if((Quadrant == 1) or (Quadrant == 2)):
    NewRow = row
    NewColumn = 2 * column
  if((Quadrant == 3) or (Quadrant == 4)):
    NewRow = row - (nrowsold / 2)
    NewColumn = (2 * column) + 1
  if((NewRow >= nrowsnew) or (NewRow < 0)):
    print "\tError in interdigitation: row", row, "maps to", NewRow, " which is out of range."
  if((NewColumn >= ncolumnsnew) or (NewColumn < 0)):
    print "\tError in interdigitation: column", column, "maps to", NewColumn, " which is out of range."
  return NewRow, NewColumn

# Fix the column offset of the reconstructed image by pushing the odd columns down by some numnber
# of pixels.
def FixSpectroCCDPixelOffset(pixelshift, row, column, npixelsincolumn):
  # Check to see if we are in an odd column, and increment the row number by one (shifting it down
  # in the immage) if we are.
  if((column % 2) == 1):
    # Shift up for the odd columns...
    NewRow = row + pixelshift
  else:
    NewRow = row
  # Now, fix any roll-over issues we might have.
  if(NewRow < 0):
    NewRow += npixelsincolumn
  if(NewRow >= npixelsincolumn):
    NewRow -= npixelsincolumn
  return NewRow

# A progress report to let me know that this thing is still running...
def Progress(thispixel, totalpixels):
  step = totalpixels / 10
  if((thispixel % step) == 0): 
    print "\t\tProcessed", thispixel, "out of", totalpixels, "pixels (" + str(int(100. * float(thispixel) / float(totalpixels))) + "%)."
  return

def GetOneGausFitModel(fitmodelname, templatehisto, mean, sigm):
  MeanHalfWindow = 100.
  LoFrac =  0.1
  HiFrac =  1.5
  FitModelString  = "[0] + (([1] * exp(-1. * (((x - [2]) / (1.414 * [3]))^2.))))"
  
  FitModel = ROOT.TF1(fitmodelname, FitModelString, 
                      templatehisto.GetXaxis().GetXmin(), 
                      templatehisto.GetXaxis().GetXmax())
  FitModel.SetLineColor(templatehisto.GetLineColor())
  FitModel.SetLineStyle(2)
  FitModel.SetLineWidth(templatehisto.GetLineWidth() + 1)
# Constant offset
  FitModel.SetParName(  0, "Offset")
  FitModel.SetParameter(0, 1.)
  FitModel.SetParLimits(0, 0., 1.e10)
  # Low-mean peak normalization
  FitModel.SetParName(  1, "Norm.")
  FitModel.SetParameter(1, templatehisto.GetMaximum())
  FitModel.SetParLimits(1, 0., 2. * templatehisto.GetMaximum())
  # Low-mean peak mean
  FitModel.SetParName(  2, "Mean")
  FitModel.SetParameter(2, mean)
  FitModel.SetParLimits(2, mean - MeanHalfWindow, mean + MeanHalfWindow)
  # Low-mean peak sigma
  FitModel.SetParName(  3, "Sigma")
  FitModel.SetParameter(3, sigm)
  FitModel.SetParLimits(3, LoFrac * sigm, HiFrac * sigm)
  return FitModel

def GetOneGausFitComponents(fitmodel):
  # Grab the peak without the offset...
  FMPeak = ROOT.TF1("FMPeak", "([1] * exp(-1. * (((x - [2]) / (1.414 * [3]))^2.)))", fitmodel.GetXmin(), fitmodel.GetXmax())
  FMPeak.SetTitle("Peak")
  FMPeak.SetLineColor(ROOT.kRed)
  FMPeak.SetLineStyle(fitmodel.GetLineStyle())
  FMPeak.FixParameter(1, fitmodel.GetParameter(1))
  FMPeak.FixParameter(2, fitmodel.GetParameter(2))
  FMPeak.FixParameter(3, fitmodel.GetParameter(3))
  return [FMPeak]

def GetTwoGausFitModel(fitmodelname, templatehisto, lomean, losigm, himean, hisigm):
  MeanHalfWindow = 50.
  LoFrac =  0.5
  HiFrac =  1.5
  FitModelString  = "[0] + (([1] * exp(-1. * (((x - [2]) / (1.414 * [3]))^2.)))) + (([4] * exp(-1. * (((x - [5]) / (1.414 * [6]))^2.))))"
  
  FitModel = ROOT.TF1(fitmodelname, FitModelString, 
                      templatehisto.GetXaxis().GetXmin(), 
                      templatehisto.GetXaxis().GetXmax())
  FitModel.SetLineColor(ROOT.kBlack)
  FitModel.SetLineStyle(2)
  FitModel.SetLineWidth(4)
# Constant offset
  FitModel.SetParName(  0, "Offset")
  FitModel.SetParameter(0, 1.)
  FitModel.SetParLimits(0, 0., 1.e10)
  # Low-mean peak normalization
  FitModel.SetParName(  1, "Low Norm.")
  FitModel.SetParameter(1, 1.e4)
  FitModel.SetParLimits(1, 0., 1.e10)
  # Low-mean peak mean
  FitModel.SetParName(  2, "Low Mean")
  FitModel.SetParameter(2, lomean)
  FitModel.SetParLimits(2, lomean - MeanHalfWindow, lomean + MeanHalfWindow)
  # Low-mean peak sigma
  FitModel.SetParName(  3, "Low Sigma")
  FitModel.SetParameter(3, losigm)
  FitModel.SetParLimits(3, LoFrac * losigm, HiFrac * losigm)
  # High-mean peak normalization
  FitModel.SetParName(  4, "High Norm.")
  FitModel.SetParameter(4, 1.e3)
  FitModel.SetParLimits(4, 0., 1.e10)
  # High-mean peak mean
  FitModel.SetParName(  5, "High Mean")
  FitModel.SetParameter(5, himean)
  FitModel.SetParLimits(5, himean - MeanHalfWindow, himean + MeanHalfWindow)
  # High-mean peak sigma
  FitModel.SetParName(  6, "High Sigma")
  FitModel.SetParameter(6, hisigm)
  FitModel.SetParLimits(6, LoFrac * hisigm, HiFrac * hisigm)
  return FitModel

# Construct and return two TF1 objects that correspond to the two scaled Poisson distributions we
# are using to describe the SPE spectrum.
def GetTwoGausFitComponents(fitmodel):
  # First, the low-mean peak:
  FMLowPeak = ROOT.TF1("FMLowPeak", "([1] * exp(-1. * (((x - [2]) / (1.414 * [3]))^2.)))", fitmodel.GetXmin(), fitmodel.GetXmax())
  FMLowPeak.SetTitle("Low-Mean Peak")
  FMLowPeak.SetLineColor(ROOT.kRed)
  FMLowPeak.SetLineStyle(fitmodel.GetLineStyle())
  FMLowPeak.FixParameter(1, fitmodel.GetParameter(1))
  FMLowPeak.FixParameter(2, fitmodel.GetParameter(2))
  FMLowPeak.FixParameter(3, fitmodel.GetParameter(3))
  # And the mid-mean peak:
  FMHighPeak = ROOT.TF1("FMHighPeak", "([4] * exp(-1. * (((x - [5]) / (1.414 * [6]))^2.)))", fitmodel.GetXmin(), fitmodel.GetXmax())
  FMHighPeak.SetTitle("High-Mean Peak")
  FMHighPeak.SetLineColor(ROOT.kBlue)
  FMHighPeak.SetLineStyle(fitmodel.GetLineStyle())
  FMHighPeak.FixParameter(4, fitmodel.GetParameter(4))
  FMHighPeak.FixParameter(5, fitmodel.GetParameter(5))
  FMHighPeak.FixParameter(6, fitmodel.GetParameter(6))
  return [FMLowPeak, FMHighPeak]

# Construct a peak model taken from RadWare, a tool often used in HPGe detector analysis...
def GetRWFitModel(fitmodelname, templatehisto, mean, sigm):
  # Set some basic parameter limits...
  MeanHalfWindow = 100.
  LoFrac =  0.5
  HiFrac =  1.5
  # Build up the peak model
  GausString = "([0] * exp(-0.5 * ((x - [1]) / [2])^2))"
  SkSfString = "([3] * TMath::Erfc((x - [1]) / (sqrt(2.) * [2])))"
  BkGdString = "[4] + ([5] * x) + ([6] * (x^2))"
  PeakModelString = GausString + " + " + SkSfString + " + " + BkGdString
  PeakModel = ROOT.TF1("PeakModel", PeakModelString, 
                       templatehisto.GetXaxis().GetXmin(), templatehisto.GetXaxis().GetXmax())
  PeakModel.SetLineColor(templatehisto.GetLineColor())
  PeakModel.SetLineStyle(2)
  PeakModel.SetLineWidth(4)
  # Calculate the initial guesses for the model parameters from the histogram
  templatehisto.GetXaxis().SetRangeUser(mean - (5. * sigm), mean + (5. * sigm))
  SpecMax = templatehisto.GetMaximum()
  templatehisto.GetXaxis().UnZoom()
  # Set up the peak model...
  # Gaussian bit:
  PeakModel.SetParName(  0, "Gaus. Nor.")
  PeakModel.SetParLimits(0, 0., 2. * SpecMax)
  PeakModel.SetParameter(0, SpecMax)
  PeakModel.SetParName(  1, "Peak Mean")
  PeakModel.SetParLimits(1, mean - MeanHalfWindow, mean + MeanHalfWindow)
  PeakModel.SetParameter(1, mean)
  PeakModel.SetParName(  2, "Gaus. sig.")
  PeakModel.SetParLimits(2, LoFrac * sigm, HiFrac * sigm)
  PeakModel.SetParameter(2, sigm)
  # Sigmoid function:
  PeakModel.SetParName(  3, "SF Nor.")
  PeakModel.SetParLimits(3, 0., 0.5 * SpecMax)
  PeakModel.SetParameter(3, 0.)
  # Polynomial background:
  PeakModel.SetParName(  4, "BG Cnst.")
  PeakModel.SetParLimits(4, 0., 2. * SpecMax)
  PeakModel.SetParameter(4, templatehisto.GetBinContent(templatehisto.FindBin(mean - 10.)))
  PeakModel.SetParName(  5, "BG Lin.")
  PeakModel.FixParameter(5, 0.)
  PeakModel.SetParName(  6, "BG Quad.")
  PeakModel.FixParameter(6, 0.)
  return PeakModel

# And get the components of the RadWare peak model...
def GetRWFitModelComponents(fitmodel):
  # Peak model components...
  GausString = "([0] * exp(-0.5 * ((x - [1]) / [2])^2))"
  SkSfString = "([3] * TMath::Erfc((x - [1]) / (sqrt(2.) * [2])))"
  BkGdString = "[4] + ([5] * x) + ([6] * (x^2))"
  # Isolate the Gaussian component of the fit model
  GausModel = ROOT.TF1("GausModel", GausString, fitmodel.GetXmin(), fitmodel.GetXmax())
  GausModel.SetTitle("Gaussian Peak")
  GausModel.SetLineColor(fitmodel.GetLineColor() - 1)
  GausModel.SetLineWidth(fitmodel.GetLineWidth())
  GausModel.SetLineStyle(fitmodel.GetLineStyle())
  GausModel.FixParameter(0, fitmodel.GetParameter(0))
  GausModel.FixParameter(1, fitmodel.GetParameter(1))
  GausModel.FixParameter(2, fitmodel.GetParameter(2))
  # Isolate the sigmoid component
  SgmdModel = ROOT.TF1("SkGsModel", SkSfString, fitmodel.GetXmin(), fitmodel.GetXmax())
  SgmdModel.SetTitle("Sigmoid Fcn.")
  SgmdModel.SetLineColor(fitmodel.GetLineColor() + 1)
  SgmdModel.SetLineWidth(fitmodel.GetLineWidth())
  SgmdModel.SetLineStyle(fitmodel.GetLineStyle())
  SgmdModel.FixParameter(3, fitmodel.GetParameter(3))
  SgmdModel.FixParameter(1, fitmodel.GetParameter(1))
  SgmdModel.FixParameter(2, fitmodel.GetParameter(2))
  # Isolate the sigmoid component
  BkGdModel = ROOT.TF1("BkGdModel", BkGdString, fitmodel.GetXmin(), fitmodel.GetXmax())
  BkGdModel.SetTitle("Pol. Bg.")
  BkGdModel.SetLineColor(fitmodel.GetLineColor() + 2)
  BkGdModel.SetLineWidth(fitmodel.GetLineWidth())
  BkGdModel.SetLineStyle(fitmodel.GetLineStyle())
  BkGdModel.FixParameter(4, fitmodel.GetParameter(4))
  BkGdModel.FixParameter(5, fitmodel.GetParameter(5))
  BkGdModel.FixParameter(6, fitmodel.GetParameter(6))
  return [GausModel, SgmdModel, BkGdModel]

# Create and return ROOT TGraphErrors object from arrays containing the some quantity as a function of another.
def CreateTGraph(xarray, yarray, xerrarray, yerrarray, name, title, color, xaxtitle, yaxtitle):
  # Create and setup the TGraph object
  AxisTitleSize = 0.05
  AxisTitleOffset = 0.7
  AxisLabelSize = 0.03
  thisGraph = ROOT.TGraphErrors(len(xarray), xarray, yarray, xerrarray, yerrarray)
  thisGraph.SetName(name)
  thisGraph.SetTitle(title)
  thisGraph.SetMarkerStyle(20)
  thisGraph.SetMarkerSize(1.2)
  thisGraph.SetMarkerColor(color)
  thisGraph.SetLineStyle(1)
  thisGraph.SetLineWidth(1)
  thisGraph.SetLineColor(color)
  thisGraph.GetXaxis().SetTitle(xaxtitle)
  thisGraph.GetXaxis().SetTitleSize(AxisTitleSize)
  thisGraph.GetXaxis().SetTitleOffset(AxisTitleOffset)
  thisGraph.GetXaxis().SetLabelSize(AxisLabelSize)
  thisGraph.GetYaxis().SetTitle(yaxtitle)
  thisGraph.GetYaxis().SetTitleSize(AxisTitleSize)
  thisGraph.GetYaxis().SetTitleOffset(1.0 * AxisTitleOffset)
  thisGraph.GetYaxis().SetLabelSize(AxisLabelSize)
  return thisGraph

# Create a TH1D object for pixel value histograms of various sorts.
def MakePixValHisto(histoname, histotitle, nbins, xlo, xhi, color):
  AxisTitleSize = 0.05
  AxisTitleOffset = 0.7
  AxisLabelSize = 0.03
  PixValHisto = ROOT.TH1D(histoname, histotitle, nbins, xlo, xhi)
  PixValHisto.SetLineColor(color)
  PixValHisto.GetXaxis().SetTitle("Background Corrected ADC Value")
  PixValHisto.GetXaxis().SetTitleSize(AxisTitleSize)
  PixValHisto.GetXaxis().SetTitleOffset(AxisTitleOffset)
  PixValHisto.GetXaxis().SetLabelSize(AxisLabelSize)
  BinWidth = (xhi - xlo) / float(nbins)
  TitleString = "Counts per " + "{:0.1f}".format(BinWidth) + " ADC Unit Bin"
  PixValHisto.GetYaxis().SetTitle(TitleString)
  PixValHisto.GetYaxis().SetTitleSize(AxisTitleSize)
  PixValHisto.GetYaxis().SetTitleOffset(1.0 * AxisTitleOffset)
  PixValHisto.GetYaxis().SetLabelSize(AxisLabelSize)
  return PixValHisto

# Create an annotation to display the parameters from the single-Gaussian fit we do to the pixel value data.
def MakeOneGausFitAnnotation(fitmodel):
  thisChi2 = fitmodel.GetChisquare()
  thisNDF  = fitmodel.GetNDF()
  if(thisNDF == 0): thisNDF = 1
  thisPVal = fitmodel.GetProb()
  Mean = fitmodel.GetParameter(2)
  MeEr = fitmodel.GetParError(2)
  Sigm = fitmodel.GetParameter(3)
  SiEr = fitmodel.GetParError(3)
  AnnotationLeft  = 0.672
  AnnotationRight = 0.972
  AnnotationTop   = 0.915
  AnnotationBottom = 0.715
  thisAnnotation = ROOT.TPaveText(AnnotationLeft,AnnotationBottom,AnnotationRight,AnnotationTop,"blNDC")
  thisAnnotation.SetName(fitmodel.GetName() + "_AnnotationText")
  thisAnnotation.SetBorderSize(1)
  thisAnnotation.SetTextFont(42)
  thisAnnotation.SetFillColor(ROOT.kWhite)
  ThisLine = "#chi^{2} per DoF = " + "{:6.1f}".format(thisChi2) + " / " + str(thisNDF) + " = " + "{:6.2f}".format(thisChi2 / float(thisNDF))
  thisAnnotation.AddText(ThisLine)
  ThisLine = "(Probability = " + "{:2.6f}".format(thisPVal) + ")"
  thisAnnotation.AddText(ThisLine)
  ThisLine = "Mean = "    + "{:6.2f}".format(Mean) + " #pm " + "{:1.2f}".format(MeEr)
  thisAnnotation.AddText(ThisLine)
  ThisLine = "Sigma =  "  + "{:6.2f}".format(Sigm) + " #pm " + "{:1.2f}".format(SiEr)
  thisAnnotation.AddText(ThisLine)
  return thisAnnotation

# Create an annotation to display the parameters from the double-Gaussian fit we do to the pixel value data.
def MakeTwoGausFitAnnotation(fitmodel):
  thisChi2 = fitmodel.GetChisquare()
  thisNDF  = fitmodel.GetNDF()
  if(thisNDF == 0): thisNDF = 1
  thisPVal = fitmodel.GetProb()
  LoMean = fitmodel.GetParameter(2)
  LoMeEr = fitmodel.GetParError(2)
  LoSigm = fitmodel.GetParameter(3)
  LoSiEr = fitmodel.GetParError(3)
  HiMean = fitmodel.GetParameter(5)
  HiMeEr = fitmodel.GetParError(5)
  HiSigm = fitmodel.GetParameter(6)
  HiSiEr = fitmodel.GetParError(6)
  AnnotationLeft  = 0.672
  AnnotationRight = 0.972
  AnnotationTop   = 0.915
  AnnotationBottom = 0.515
  thisAnnotation = ROOT.TPaveText(AnnotationLeft,AnnotationBottom,AnnotationRight,AnnotationTop,"blNDC")
  thisAnnotation.SetName(fitmodel.GetName() + "_AnnotationText")
  thisAnnotation.SetBorderSize(1)
  thisAnnotation.SetTextFont(42)
  thisAnnotation.SetFillColor(ROOT.kWhite)
  ThisLine = "#chi^{2} per DoF = " + "{:6.1f}".format(thisChi2) + " / " + str(thisNDF) + " = " + "{:6.2f}".format(thisChi2 / float(thisNDF))
  thisAnnotation.AddText(ThisLine)
  ThisLine = "(Probability = " + "{:2.6f}".format(thisPVal) + ")"
  thisAnnotation.AddText(ThisLine)
  ThisLine = "Low Mean = "    + "{:6.2f}".format(LoMean) + " #pm " + "{:1.2f}".format(LoMeEr)
  thisAnnotation.AddText(ThisLine)
  ThisLine = "Low Sigma =  "  + "{:6.2f}".format(LoSigm) + " #pm " + "{:1.2f}".format(LoSiEr)
  thisAnnotation.AddText(ThisLine)
  ThisLine = "High Mean = "   + "{:6.2f}".format(HiMean) + " #pm " + "{:1.2f}".format(HiMeEr)
  thisAnnotation.AddText(ThisLine)
  ThisLine = "High Sigma =  " + "{:6.2f}".format(HiSigm) + " #pm " + "{:1.2f}".format(HiSiEr)
  thisAnnotation.AddText(ThisLine)
  return thisAnnotation

# Create an annotation to display the parameters from the Radware fit
def MakeFitAnnotationRW(fitmodel):
  thisChi2 = fitmodel.GetChisquare()
  thisNDF  = fitmodel.GetNDF()
  if(thisNDF == 0): thisNDF = 1
  thisPVal = fitmodel.GetProb()
  Gnor = fitmodel.GetParameter(0)
  GnEr = fitmodel.GetParError(0)
  Mean = fitmodel.GetParameter(1)
  MeEr = fitmodel.GetParError(1)
  Sigm = fitmodel.GetParameter(2)
  SiEr = fitmodel.GetParError(2)
  SmdN = fitmodel.GetParameter(3)
  SNEr = fitmodel.GetParError(3)
  AnnotationLeft  = 0.672
  AnnotationRight = 0.972
  AnnotationTop   = 0.915
  AnnotationBottom = 0.515
  thisAnnotation = ROOT.TPaveText(AnnotationLeft,AnnotationBottom,AnnotationRight,AnnotationTop,"blNDC")
  thisAnnotation.SetTextFont(42)
  thisAnnotation.SetName(fitmodel.GetName() + "_AnnotationText")
  thisAnnotation.SetBorderSize(1)
  thisAnnotation.SetFillColor(ROOT.kWhite)
  ThisLine = "#chi^{2} per DoF = " + "{:6.1f}".format(thisChi2) + " / " + str(thisNDF) + " = " + "{:6.2f}".format(thisChi2 / float(thisNDF))
  thisAnnotation.AddText(ThisLine)
  ThisLine = "(Probability = " + "{:2.6f}".format(thisPVal) + ")"
  thisAnnotation.AddText(ThisLine)
  ThisLine = "Mean = "    + "{:6.2f}".format(Mean) + " #pm " + "{:1.2f}".format(MeEr)
  thisAnnotation.AddText(ThisLine)
  ThisLine = "Sigma =  "  + "{:6.2f}".format(Sigm) + " #pm " + "{:1.2f}".format(SiEr)
  thisAnnotation.AddText(ThisLine)
  ThisLine = "Gaus. Norm. = "   + "{:6.2f}".format(Gnor) + " #pm " + "{:1.2f}".format(GnEr)
  thisAnnotation.AddText(ThisLine)
  ThisLine = "Sigmoid Norm. = "   + "{:6.2f}".format(SmdN) + " #pm " + "{:1.2f}".format(SNEr)
  thisAnnotation.AddText(ThisLine)
  # Calculate and report the FWHM of the Gauussian and skewed Gaussian components of the fit model.
  #Components = GetRWFitModelComponents(fitmodel)
  #thisModel = ROOT.TF1("thisModel", Components[0].GetName() + " + " + Components[1].GetName(), fitmodel.GetXmin(), fitmodel.GetXmax())
  #MaxVal = thisModel.GetMaximum()
  #MaxX = thisModel.GetMaximumX()
  #xStep = (fitmodel.GetXmax() - fitmodel.GetXmin()) / 1000.
  # Get the upper side of the full width:
  #thisX = MaxX
  #CurrentVal = thisModel.Eval(thisX)
  #while(CurrentVal > (0.5 * MaxVal)):
  #  thisX += xStep
  #  CurrentVal = thisModel.Eval(thisX)
  #HiSide = thisX
  # Now get the low side of the full width:
  #thisX = MaxX
  #CurrentVal = thisModel.Eval(thisX)
  #while(CurrentVal > (0.5 * MaxVal)):
  #  thisX -= xStep
  #  CurrentVal = thisModel.Eval(thisX)
  #LoSide = thisX  
  #ThisLine = "FWHM =  " + "{:6.2f}".format(HiSide - LoSide)
  #thisAnnotation.AddText(ThisLine)
  return thisAnnotation

# Pull the profile of pixel values between xlo_mm and xhi_mm for y bin number ybin out of
# imagehisto and return a TGraph.
def GetXProfile(imagehisto, ybin, xlo_mm, xhi_mm):
  xbins = range(imagehisto.GetXaxis().FindBin(xlo_mm), imagehisto.GetXaxis().FindBin(xhi_mm) + 1)
  xvals = []
  yvals = []
  for xbin in xbins:
    xvals.append(imagehisto.GetXaxis().GetBinCenter(xbin))
    yvals.append(imagehisto.GetBinContent(xbin, ybin))
  thisGraph = ROOT.TGraph( len(xvals), array.array("f", xvals), array.array("f", yvals) )
  thisGraph.SetName(imagehisto.GetName() + "_ybin_" + str(ybin))
  thisGraph.SetTitle(imagehisto.GetTitle() + ", y = " + "{:3.1f}".format(imagehisto.GetYaxis().GetBinCenter(ybin)) + " mm")
  thisGraph.GetXaxis().SetTitle("X Position [mm]")
  thisGraph.GetXaxis().SetTitleOffset(1.1)
  thisGraph.GetYaxis().SetTitle("Pixel Value [ADC Units]")
  thisGraph.GetYaxis().SetTitleOffset(1.1)
  # Quickly calculate the weighted mean and RMS of this TGraph object.
  thisMean = 0.
  thisMeanSq = 0.
  thisTotal = 0.
  for i in range(thisGraph.GetN()):
    thisY = numpy.abs(thisGraph.GetY()[i])
    thisMean += (thisGraph.GetX()[i] * thisY)
    thisMeanSq += ((thisGraph.GetX()[i]**2.) * thisY)
    thisTotal += thisY
  thisMean /= thisTotal
  thisMeanSq /= thisTotal
  thisRMS = (thisMeanSq - (thisMean**2.))**0.5
  # And get the half-amplitude for this graph too.
  thisHalfAmpl = 0.5 * (max(yvals) - min(yvals))
  return thisGraph, thisMean, thisRMS, thisHalfAmpl

# Pull the profile of pixel values between xlo_mm and xhi_mm for y bin number ybin out of
# imagehisto and return the x value of its maximum and its and the half max range on either side.
def GetXProfileXmaxAndHalfRange(imagehisto, ybin, xlo_mm, xhi_mm):
  xbins = range(imagehisto.GetXaxis().FindBin(xlo_mm), imagehisto.GetXaxis().FindBin(xhi_mm) + 1)
  xVals = []
  PixVals = [] 
  for xbin in xbins:
    xVals.append(imagehisto.GetXaxis().GetBinCenter(xbin))
    PixVals.append(imagehisto.GetBinContent(xbin, ybin))
  # Get the baseline value by averaging the three pixels on either end of the list.
  PixValBaseLine = 0.
  for i in range(-3, 3):
    PixValBaseLine += PixVals[i] / 6.
  # Find the maximum value, its bin number, its x position, and the half-amplitude value.
  MaxPixVal = max(PixVals)
  MaxPixBin = PixVals.index(MaxPixVal)
  MaxXVal = xVals[MaxPixBin]
  HalfAmplVal = PixValBaseLine + (0.5 * (MaxPixVal - PixValBaseLine))
  # Now start from the max value bin and work up until the value falls below the half-amplitude value:
  thisBin = MaxPixBin
  nBinsBelowHalfMaxValThresh = 3
  nBinsBelowHalfMaxVal = 0
  while((nBinsBelowHalfMaxVal <= nBinsBelowHalfMaxValThresh) and (thisBin < len(PixVals) - 1)):
    thisBin += 1
    if(PixVals[thisBin] < HalfAmplVal):
      nBinsBelowHalfMaxVal += 1
    #print thisBin, PixVals[thisBin], HalfAmplVal
  HalfMaxXValHi = xVals[thisBin] - MaxXVal
  # Now reset and do the same on the low side:
  thisBin = MaxPixBin
  nBinsBelowHalfMaxVal = 0
  while((nBinsBelowHalfMaxVal <= nBinsBelowHalfMaxValThresh) and (thisBin > 0)):
    thisBin -= 1
    if(PixVals[thisBin] < HalfAmplVal):
      nBinsBelowHalfMaxVal += 1
    #print thisBin, PixVals[thisBin], HalfAmplVal
  HalfMaxXValLo = MaxXVal - xVals[thisBin]
  #print "At y =", imagehisto.GetYaxis().GetBinCenter(ybin), "mm, the maxumum is", MaxPixVal, "at x =", MaxXVal, "+", HalfMaxXValHi, "-", HalfMaxXValLo, "mm."
  #exit()
  return MaxXVal, HalfMaxXValHi, HalfMaxXValLo, HalfAmplVal


