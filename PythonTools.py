#!/usr/bin/python

###################################################################################################
# Support functions for fits file analysis.                                                       #
###################################################################################################

import ROOT

# Correct for the row and column offsets...
def FixSpectroCCDOffset(row, column, nrows, ncolumns, rowoffset, columnoffset):
  NewRow = row - rowoffset
  if(NewRow < 0): NewRow += nrows
  NewColumn = column - columnoffset
  if(NewColumn < 0): NewColumn += ncolumns
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

# Fix the column offset of the reconstructed image by pushing the odd columns down and the even
# columns up by some numnber of pixels.
def FixSpectroCCDPixelOffset(pixelshift, row, column, npixelsincolumn):
  # First, decide if we're in an odd or even column:
  if((column % 2) == 0):
    # Shift the pixel row down by pixelshift since we are in an even column.  
    NewRow = row - pixelshift
  elif((column % 2) == 1):
    # Shift up for the odd columns...
    NewRow = row + pixelshift
  else:
    print "This column number seens to be neither odd nor even.  Whaaaaaaaaaaa?"
    exit()
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
  MeanHalfWindow = 50.
  LoFrac =  0.5
  HiFrac =  1.5
  FitModelString  = "[0] + (([1] * exp(-1. * (((x - [2]) / (1.414 * [3]))^2.))))"
  
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
  FitModel.SetParameter(1, 2.5e3)
  FitModel.SetParLimits(1, 0., 1.e10)
  # Low-mean peak mean
  FitModel.SetParName(  2, "Low Mean")
  FitModel.SetParameter(2, mean)
  FitModel.SetParLimits(2, mean - MeanHalfWindow, mean + MeanHalfWindow)
  # Low-mean peak sigma
  FitModel.SetParName(  3, "Low Sigma")
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

# Create an annotation to display the parameters from the fit we do to the pixel value data.
def MakeFitAnnotation(fitmodel):
  thisChi2 = fitmodel.GetChisquare()
  thisNDF  = fitmodel.GetNDF()
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

