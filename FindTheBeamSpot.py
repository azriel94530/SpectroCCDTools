#!/usr/bin/python

####################################################################################################
# Open up the 2D histogram of a fits image created by Fits2Root.py, then find the beam spot and do #
# some analysis.                                                                                   #
####################################################################################################

# Header, import statements etc.
import time
import sys
import ROOT
import RootPlotLibs
import PythonTools
import numpy
import os
import array

####################################
#  BEGIN MAIN BODY OF THE CODE!!!  #
####################################

# Get the start time of this calculation
StartTime = time.time()

# Get ROOT going and load a useful function or two.
ROOT.gROOT.Reset()
ROOT.gROOT.ProcessLine(".L ./CompiledTools.C+")

# Set some flags for how verbose our input and output are going to be.
Debugging = False
VerboseProcessing = True

# Figure out exactly what we're doing based on what get's passed to this thing as an argument.
if(len(sys.argv) == 2):
  NoSpecifiedRange = True
  NoOutputNameSpecified = True
  InputFilePath = sys.argv[1]
  print "\tReading in: '" + InputFilePath + "' for analysis."
elif(len(sys.argv) == 6):
  NoSpecifiedRange = False
  NoOutputNameSpecified = True
  InputFilePath = sys.argv[1]
  xLo = float(sys.argv[2])
  xHi = float(sys.argv[3])
  yLo = float(sys.argv[4])
  yHi = float(sys.argv[5])
  print "\tReading in: '" + InputFilePath + "' for analysis."
  print "\tZooming in on: ", xLo, "< x <", xHi, "and", yLo, "< y <", yHi, "mm."
elif(len(sys.argv) == 7):
  NoSpecifiedRange = False
  NoOutputNameSpecified = False
  InputFilePath = sys.argv[1]
  xLo = float(sys.argv[2])
  xHi = float(sys.argv[3])
  yLo = float(sys.argv[4])
  yHi = float(sys.argv[5])
  OutputTag = sys.argv[6]
  print "\tReading in: '" + InputFilePath + "' for analysis."
  print "\tZooming in on: ", xLo, "< x <", xHi, "and", yLo, "< y <", yHi, "mm."
  print "\tTagging output with the string, \'" + OutputTag + "\'"
else:
  print "Usage: [python] AnalyzeNoise.py path/to/fits/root/file [xRangeLo xRangeHi yRangeLo yRangeHi OutputIdentifierString]"
  exit()
# If you haven't already done so, have the user input a string to tag the output of this particular
# pixel value histogram.
if(NoOutputNameSpecified):
  OutputTag = input("\tHow about a string (IN QUOTES!!!) to tag the output of this analysis? ")
  print "\tTagging output with the string, \'" + OutputTag + "\'"

# Crack open the root file, get the 2D histogram, draw it, and zoom in on the region of interest...
InputFile = ROOT.TFile(InputFilePath)
ImageHisto = InputFile.Get("thatHistogram")
ImageHisto.SetName("ImageHisto")

# Plot the image histogram so we can see what we're doing...
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.05)
aPad.SetBottomMargin(0.08)
aPad.Draw()
aPad.cd()
if(NoSpecifiedRange):
  ImageHisto.Draw("colz")
  aCanvas.Update()
  xLo = float(input("\tx Range Low?  "))
  xHi = float(input("\tx Range High? "))
  yLo = float(input("\ty Range Low?  "))
  yHi = float(input("\ty Range High? "))
  print "\tZooming in on: ", xLo, "< x <", xHi, "and", yLo, "< y <", yHi, "mm."
ImageHisto.GetXaxis().SetRangeUser(xLo, xHi)
ImageHisto.GetYaxis().SetRangeUser(yLo, yHi)
ImageHisto.GetZaxis().UnZoom()
ImageHisto.Draw("colz")
aCanvas.Update()
aCanvas.SaveAs(InputFilePath.replace(".root", "." + OutputTag + ".png"))

# Pull in the list of bins in both X and Y we're going to look at.
Xbins = range(ImageHisto.GetXaxis().FindBin(xLo), ImageHisto.GetXaxis().FindBin(xHi))
if(Debugging): print Xbins
Ybins = range(ImageHisto.GetYaxis().FindBin(yLo), ImageHisto.GetYaxis().FindBin(yHi))
if(Debugging): print Ybins

# Calculate the mean and RMS of the pixel values in this image.
print "\tReading in pixel values from TH2D to find the beam spot..."
PixelValues = []
PVMax = -1.e6
MaxBinX = -10
MaxBinY = -10
nValues = len(Xbins) * len(Ybins)
iVal = 0
for xbin in Xbins:
  for ybin in Ybins:
    thisPV = ImageHisto.GetBinContent(xbin, ybin)
    PixelValues.append(thisPV)
    if(thisPV > PVMax):
      PVMax = thisPV
      MaxBinX = xbin
      MaxBinY = ybin
    iVal += 1
    if((nValues >= 100) and (iVal % int(nValues / 100) == 0)):
      ROOT.StatusBar(iVal, nValues, int(nValues / 100))
print
PVMean = numpy.mean(PixelValues)
PVRMS  = numpy.std(PixelValues)
print "\tPixel value mean is: " + "{:3.1f}".format(PVMean) + " +/- " + "{:0.1f}".format(PVRMS)
SpotMaxX = ImageHisto.GetXaxis().GetBinCenter(MaxBinX)
SpotMaxY = ImageHisto.GetYaxis().GetBinCenter(MaxBinY)
print "\tMaximum value is: " + "{:3.1f}".format(PVMax) + ", at x = " + "{:3.3f}".format(SpotMaxX) + ", y = " + "{:3.3f}".format(SpotMaxY)

# Now that we've found the center of the beam spot, and what the background level looks like,
# let's calculate its size.
AverageHalfRangeX = 100 # Number of bins to average on either side of the maxumum bin while
#                         looking for a return to baseline.  Corresponds to 0.5 mm.
AverageHalfRangeY =  50 # Corresponds to ~2 mm.
BacktoBGThreshX = 20 # Number of column averages that must be at background to say we've found the spot edge in the x direction.
BacktoBGThreshY = 10 # Number of row averages that must be at background to say we've found the spot edge in the y direction.
# Start at the high point, and work our way out to the low edge in the x (5 um) direction:
thisX = MaxBinX
thisY = MaxBinY
ColumnsAtBGLoX = 0
while(ColumnsAtBGLoX <= BacktoBGThreshX):
  thisX -= 1
  thisXAverage = 0.
  for i in range(-1 * AverageHalfRangeY, AverageHalfRangeY + 1):
    thisXAverage += ImageHisto.GetBinContent(thisX, thisY + i) / float(1 + (2 * AverageHalfRangeY))
  if(thisXAverage < (PVMean + (0.5 * PVRMS))): ColumnsAtBGLoX += 1
SpotLoX = thisX
if(Debugging): print "\t\tSpot x edge on low side is at", ImageHisto.GetXaxis().GetBinCenter(SpotLoX), "mm."
# Now, do the high edge in the x direction:
thisX = MaxBinX
thisY = MaxBinY
ColumnsAtBGHiX = 0
while(ColumnsAtBGHiX <= BacktoBGThreshX):
  thisX += 1
  thisXAverage = 0.
  for i in range(-1 * AverageHalfRangeY, AverageHalfRangeY + 1):
    thisXAverage += ImageHisto.GetBinContent(thisX, thisY + i) / float(1 + (2 * AverageHalfRangeY))
  if(thisXAverage < (PVMean + (0.5 * PVRMS))): ColumnsAtBGHiX += 1
SpotHiX = thisX
if(Debugging): print "\t\tSpot x edge on high side is at", ImageHisto.GetXaxis().GetBinCenter(SpotHiX), "mm."
# Find the low edge in the y (45 um) direction:
thisX = MaxBinX
thisY = MaxBinY
RowsAtBGLoY = 0
while(RowsAtBGLoY <= BacktoBGThreshY):
  thisY -= 1
  thisYAverage = 0.
  for i in range(-1 * AverageHalfRangeX, AverageHalfRangeX + 1):
    thisYAverage += ImageHisto.GetBinContent(thisX + i, thisY) / float(1 + (2 * AverageHalfRangeY))
  if(thisYAverage < (PVMean + (0.5 * PVRMS))): RowsAtBGLoY += 1
SpotLoY = thisY
if(Debugging): print "\t\tSpot y edge on low side is at", ImageHisto.GetYaxis().GetBinCenter(SpotLoY), "mm."
# And last, yind the high edge in y:
thisX = MaxBinX
thisY = MaxBinY
RowsAtBGHiY = 0
while(RowsAtBGHiY <= BacktoBGThreshY):
  thisY += 1
  thisYAverage = 0.
  for i in range(-1 * AverageHalfRangeX, AverageHalfRangeX + 1):
    thisYAverage += ImageHisto.GetBinContent(thisX + i, thisY) / float(1 + (2 * AverageHalfRangeY))
  if(thisYAverage < (PVMean + (0.5 * PVRMS))): RowsAtBGHiY += 1
SpotHiY = thisY
if(Debugging): print "\t\tSpot y edge on low side is at", ImageHisto.GetYaxis().GetBinCenter(SpotHiY), "mm."

# Report the spot dimensions.
SpotLoX_mm = ImageHisto.GetXaxis().GetBinCenter(SpotLoX)
SpotHiX_mm = ImageHisto.GetXaxis().GetBinCenter(SpotHiX)
SpotLoY_mm = ImageHisto.GetYaxis().GetBinCenter(SpotLoY)
SpotHiY_mm = ImageHisto.GetYaxis().GetBinCenter(SpotHiY)
print "\tBeam spot extends from", "{:3.3f}".format(SpotLoX_mm), "< x <", "{:3.3f}".format(SpotHiX_mm), "mm and", "{:3.3f}".format(SpotLoY_mm), "< y <", "{:3.3f}".format(SpotHiY_mm), "mm (or", "{:3.3f}".format(SpotHiX_mm - SpotLoX_mm), "by", "{:3.3f}".format(SpotHiY_mm - SpotLoY_mm), "mm)."

# OK, now that we've found the beam spot, let's go ahead and extract its profile in x as a function of y.  
ProfileGraphs = []
ProfGraMeans = []
ProfGraRMSs = []
Ybins = range(SpotLoY, SpotHiY + 1)
YValues = []
Zeros = []
SpotHalfAmplVsY = []
SpotLocGraphs = []
for thisYbin in Ybins:
  YValues.append(ImageHisto.GetYaxis().GetBinCenter(thisYbin))
  Zeros.append(0.)
  thisProfileGraph, thisXmean, thisXrms, thisHalfAmpl = PythonTools.GetXProfile(ImageHisto, thisYbin, SpotLoX_mm, SpotHiX_mm)
  ProfileGraphs.append(thisProfileGraph)
  ProfGraMeans.append(thisXmean)
  ProfGraRMSs.append(0.5 * thisXrms)
  SpotHalfAmplVsY.append(thisHalfAmpl)
# Plot us some profiles!
print "\tPlotting", len(ProfileGraphs), "x profiles..."
ROOT.gStyle.SetOptTitle(0)
aPad.SetRightMargin(0.01)
aPad.SetLeftMargin(0.08)
aPad.SetTopMargin(0.01)
PlotFileName = InputFilePath.replace(".root", "." + OutputTag + ".BeamSpotXProfVsY.gif")
if os.path.isfile(PlotFileName):
  #print "Removing old version of", PlotFileName
  os.system("rm " + PlotFileName)
Annotations = []
MeanXGraphs = []
for i in range(len(ProfileGraphs)):
  # Regularize the limits of this plot and draw it.
  ProfileGraphs[i].GetXaxis().SetRangeUser(SpotLoX_mm, SpotHiX_mm)
  ProfileGraphs[i].GetYaxis().SetRangeUser(-0.15 * PVMax, 1.05 * PVMax)
  ProfileGraphs[i].Draw("alp")
  # Make an annotation to denote the y position of this x profile.
  Annotations.append(ROOT.TPaveText(0.892,0.88,0.987,0.97,"blNDC"))
  Annotations[i].SetName("TimeStamp")
  Annotations[i].SetBorderSize(0)
  Annotations[i].SetFillColor(ROOT.kWhite)
  Annotations[i].AddText("y = " + "{:2.3f}".format(ImageHisto.GetYaxis().GetBinCenter(Ybins[i])) + " mm")
  Annotations[i].Draw()
  # Now mark the maximum value with a TGraph object.
  MeanXGraphs.append(ROOT.TGraphErrors(1, 
                                       array.array("f", [ProfGraMeans[i]]), 
                                       array.array("f", [SpotHalfAmplVsY[i]]),
                                       array.array("f", [ProfGraRMSs[i]]),
                                       array.array("f", [0.])))
  MeanXGraphs[-1].SetMarkerStyle(20)
  MeanXGraphs[-1].SetMarkerSize(2)
  MeanXGraphs[-1].SetMarkerColor(ROOT.kRed)
  MeanXGraphs[-1].SetLineWidth(2)
  MeanXGraphs[-1].SetLineColor(ROOT.kRed)
  MeanXGraphs[-1].Draw("samep")
  # Write this frame to the animated gif.
  aCanvas.Update()
  aPad.Print(PlotFileName + "+", "gif+01")

# OK, now that's done, let's zoom in on the beam spot region and make a coulpe of plots.  First,
# a quick zoom in of the plot we already made and then draw the y vs. x profile on top of it:
ROOT.gStyle.SetOptTitle(1)
aPad.SetTopMargin(0.09)
aPad.SetRightMargin(0.11)
aPad.SetLeftMargin(0.05)
ImageHisto.GetXaxis().SetRangeUser(SpotLoX_mm, SpotHiX_mm)
ImageHisto.GetYaxis().SetRangeUser(SpotLoY_mm, SpotHiY_mm)
ImageHisto.Draw("colz")
# Just for fun, let's also mark the mean/RMS profile too.
SpotMeanProfile = ROOT.TGraphErrors(len(ProfGraMeans),
                                    array.array("f", ProfGraMeans),
                                    array.array("f", YValues),
                                    array.array("f", ProfGraRMSs),
                                    array.array("f", Zeros))
SpotMeanProfile.SetMarkerStyle(20)
SpotMeanProfile.SetMarkerSize(2)
SpotMeanProfile.SetMarkerColor(ROOT.kBlack)
SpotMeanProfile.SetLineWidth(2)
SpotMeanProfile.SetLineColor(ROOT.kBlack)
SpotMeanProfile.Draw("samep")
PlotFileName = InputFilePath.replace(".root", "." + OutputTag + ".zoom.colz.png")
aCanvas.SaveAs(PlotFileName)
# Now, make a nice, photogenic surface plot:
ImageHisto.GetXaxis().SetTitleOffset(1.5)
ImageHisto.GetYaxis().SetTitleOffset(1.6)
ImageHisto.GetZaxis().SetTitle("Pixel Value [ADC Units]")
ImageHisto.GetZaxis().SetTitleOffset(1.4)
aPad.SetLeftMargin(0.10)
ImageHisto.Draw("surf3")
aCanvas.Update()
PlotFileName = InputFilePath.replace(".root", "." + OutputTag + ".zoom.surf3.png")
aCanvas.SaveAs(PlotFileName)

# Now calculate the weighted average x position of the spot for +/- 0.5 mm of the maximum.
SpotXAvgHalfRange = 0.5 #[mm]
SpotXAvg = 0.
SpotXAvgUnc = 0.
nPointsInSpotXAvg = 0
for i in range(SpotMeanProfile.GetN()):
  if((SpotMeanProfile.GetY()[i] > (SpotMaxY - SpotXAvgHalfRange)) and 
     (SpotMeanProfile.GetY()[i] < (SpotMaxY + SpotXAvgHalfRange))):
    SpotXAvg += SpotMeanProfile.GetX()[i]
    SpotXAvgUnc += SpotMeanProfile.GetEX()[i]
    nPointsInSpotXAvg += 1
SpotXAvg /= float(nPointsInSpotXAvg)
SpotXAvgUnc /= float(nPointsInSpotXAvg)
print "\tWeighted average spot position is at x = " + "{:2.3f}".format(SpotXAvg) + " +/-" + "{:2.3f}".format(SpotXAvgUnc), "mm for y = " + "{:2.3f}".format(SpotMaxY) + " +/- " + "{:2.3f}".format(SpotXAvgHalfRange) + " mm."

# Now that we've calculated the weighted average of each x-slice through the beam spot as a
# function of y as well as the weighted average of the beamspot near its maximum, we can stack all
# those y slices up such that their weighted averages all line up with one another.
aPad.SetLeftMargin(0.08)
aPad.SetRightMargin(0.02)
xPixelPitch_mm = 0.005
nBins = int((SpotHiX_mm - SpotLoX_mm) / xPixelPitch_mm) + 1
BeamSpotXProf = ROOT.TH1D("BeamSpotXProf", "Corrected Beamspot Profile in X", nBins, SpotLoX_mm, SpotHiX_mm)
BeamSpotXProf.GetXaxis().SetTitle("Corrected X Position [mm]")
BeamSpotXProf.GetYaxis().SetTitle("Projected Spot Profile [ADC Units]")
BeamSpotXProf.GetYaxis().SetTitleOffset(1.2)
BeamSpotXProf.SetLineColor(ROOT.kBlue)
BeamSpotXProf.SetLineWidth(2)
for i in range(len(ProfileGraphs)):
  thisOffset = SpotXAvg - ProfGraMeans[i]
  for j in range(ProfileGraphs[i].GetN()):
    thisXVal = ProfileGraphs[i].GetX()[j] + thisOffset
    thisYVal = ProfileGraphs[i].GetY()[j]
    BeamSpotXProf.Fill(thisXVal, thisYVal)
BeamSpotXProf.Draw()
aCanvas.Update()
PlotFileName = InputFilePath.replace(".root", "." + OutputTag + ".BeamSpotXProf.pdf")
aCanvas.SaveAs(PlotFileName)

# Finally, let's draw a heat map plot that is actally at the correct aspect ratio.
AspectRatio = (SpotHiX_mm - SpotLoX_mm) / (SpotHiY_mm - SpotLoY_mm)
del aPad
del aCanvas
ROOT.gStyle.SetOptTitle(0)
YPlotHeight = 1000.
XPlotHeight = YPlotHeight * AspectRatio
aCanvas = ROOT.TCanvas("aCanvas","Look!  It's a Canvas!",0,0,int(XPlotHeight),int(YPlotHeight))
aCanvas.SetHighLightColor(ROOT.kWhite)
aCanvas.SetBorderSize(0)
aCanvas.SetGridx(0)
aCanvas.SetGridy(0)
aCanvas.SetFrameFillColor(ROOT.kWhite)
aCanvas.SetFillColor(ROOT.kWhite)
aCanvas.Draw()
aCanvas.cd()
aPad = RootPlotLibs.ASimplePad()
aPad.SetLeftMargin(  0.01)
aPad.SetTopMargin(   0.001)
aPad.SetRightMargin( 0.01)
aPad.SetBottomMargin(0.001)
aPad.Draw()
aPad.cd()
ImageHisto.Draw("colz")
aCanvas.Update()
PlotFileName = InputFilePath.replace(".root", "." + OutputTag + ".zoom.TrueAR.png")
aCanvas.SaveAs(PlotFileName)

# Now that we're done with ImageHisto, close the file it came from.
InputFile.Close()

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
