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

# Interdigitate the 
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

# A progress report to let me know that this thing is still running...
def Progress(thispixel, totalpixels):
  step = totalpixels / 10
  if((thispixel % step) == 0): 
    print "\t\tProcessed", thispixel, "out of", totalpixels, "pixels (" + str(int(100. * float(thispixel) / float(totalpixels))) + "%)."
  return

def GetFitModel(fitmodelname, templatehisto, lomean, losigm, mimean, misigm, himean, hisigm):
  MeanHalfWindow = 50.
  LoFrac =  0.5
  HiFrac =  1.5
  FitModelString  = "[0] + (([1] * exp(-1. * (((x - [2]) / (1.414 * [3]))^2.)))) + (([4] * exp(-1. * (((x - [5]) / (1.414 * [6]))^2.)))) + (([7] * exp(-1. * (((x - [8]) / (1.414 * [9]))^2.))))"
  
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
  # mid-mean peak normalization
  FitModel.SetParName(  4, "Mid Norm.")
  FitModel.SetParameter(4, 5.e3)
  FitModel.SetParLimits(4, 0., 1.e10)
  # Mid-mean peak mean
  FitModel.SetParName(  5, "Mid Mean")
  FitModel.SetParameter(5, mimean)
  FitModel.SetParLimits(5, mimean - MeanHalfWindow, mimean + MeanHalfWindow)
  # Mid-mean peak sigma
  FitModel.SetParName(  6, "Mid Sigma")
  FitModel.SetParameter(6, misigm)
  FitModel.SetParLimits(6, LoFrac * misigm, HiFrac * misigm)
  # High-mean peak normalization
  FitModel.SetParName(  7, "High Norm.")
  FitModel.SetParameter(7, 1.e3)
  FitModel.SetParLimits(7, 0., 1.e10)
  # High-mean peak mean
  FitModel.SetParName(  8, "High Mean")
  FitModel.SetParameter(8, himean)
  FitModel.SetParLimits(8, himean - MeanHalfWindow, himean + MeanHalfWindow)
  # High-mean peak sigma
  FitModel.SetParName(  9, "High Sigma")
  FitModel.SetParameter(9, hisigm)
  FitModel.SetParLimits(9, LoFrac * hisigm, HiFrac * hisigm)
  return FitModel

# Construct and return two TF1 objects that correspond to the two scaled Poisson distributions we
# are using to describe the SPE spectrum.
def GetFitComponents(fitmodel):
  # First, the low-mean peak:
  FMLowPeak = ROOT.TF1("FMLowPeak", "([1] * exp(-1. * (((x - [2]) / (1.414 * [3]))^2.)))", fitmodel.GetXmin(), fitmodel.GetXmax())
  FMLowPeak.SetTitle("Low-Mean Peak")
  FMLowPeak.SetLineColor(ROOT.kRed)
  FMLowPeak.SetLineStyle(fitmodel.GetLineStyle())
  FMLowPeak.FixParameter(1, fitmodel.GetParameter(1))
  FMLowPeak.FixParameter(2, fitmodel.GetParameter(2))
  FMLowPeak.FixParameter(3, fitmodel.GetParameter(3))
  # And the mid-mean peak:
  FMMidPeak = ROOT.TF1("FMMidPeak", "([4] * exp(-1. * (((x - [5]) / (1.414 * [6]))^2.)))", fitmodel.GetXmin(), fitmodel.GetXmax())
  FMMidPeak.SetTitle("Mid-Mean Peak")
  FMMidPeak.SetLineColor(ROOT.kGreen - 1)
  FMMidPeak.SetLineStyle(fitmodel.GetLineStyle())
  FMMidPeak.FixParameter(4, fitmodel.GetParameter(4))
  FMMidPeak.FixParameter(5, fitmodel.GetParameter(5))
  FMMidPeak.FixParameter(6, fitmodel.GetParameter(6))
  # And the high-mean peak:
  FMHighPeak = ROOT.TF1("FMHighPeak", "([7] * exp(-1. * (((x - [8]) / (1.414 * [9]))^2.)))", fitmodel.GetXmin(), fitmodel.GetXmax())
  FMHighPeak.SetTitle("High-Mean Peak")
  FMHighPeak.SetLineColor(ROOT.kBlue)
  FMHighPeak.SetLineStyle(fitmodel.GetLineStyle())
  FMHighPeak.FixParameter(7, fitmodel.GetParameter(7))
  FMHighPeak.FixParameter(8, fitmodel.GetParameter(8))
  FMHighPeak.FixParameter(9, fitmodel.GetParameter(9))
  return [FMLowPeak, FMMidPeak, FMHighPeak]
