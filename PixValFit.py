#!/Users/vmgehman/anaconda/bin/python

####################################################################################################
# Open up the histogram of pixel values created by Fits2Root.py and do a sensible fit to that      #
# business...  There will probably be a more exciting analysis soon, but this is a fun place to    #
# start.                                                                                           #
####################################################################################################

# Header, import statements etc.
import time
import sys
import ROOT
import RootPlotLibs
import PythonTools
import numpy

####################################
#  BEGIN MAIN BODY OF THE CODE!!!  #
####################################

# Get the start time of this calculation
StartTime = time.time()

# Set some flags for how verbose our input and output are going to be.
Debugging = False
VerboseProcessing = True

if(len(sys.argv) != 3):
  print "Usage: python PixValFit.py path/to/root/file/with/pixel/value/histogram N"
  print "(Where \"N\" is the number of Gaussians you want to fit to things.  Right now, N can equal 1 or 2)"
  exit()

# Pull in the path to the root file we're going to look at
InputFilePath = sys.argv[1]
if(VerboseProcessing): 
  print "\tReading in: '" + InputFilePath + "' for analysis."

# And pull in the number of Gaussians we're going to fit.
nPeaks = int(sys.argv[2])
if(VerboseProcessing): 
  print "\tFitting", nPeaks, "Gaussian function(s) to the pixel value histogram."

# Crack open the file, get the pixel value histogram...
InputFile = ROOT.TFile(InputFilePath)
PixValHisto = InputFile.Get("PixelValueHistoZoom")
PixValHisto.SetLineColor(ROOT.kBlack)

# Go ahead and plot this thing now...
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.08)
aPad.SetRightMargin(0.01)
aPad.SetBottomMargin(0.08)
aPad.SetLogy(0)
aPad.Draw()
aPad.cd()
PixValHisto.Draw()
aCanvas.Update()

# Create the appropriate fit model, do the fit, and plot the components separately.
if(nPeaks == 1):
  FitModel = PythonTools.GetOneGausFitModel("OneGausFit", PixValHisto, 0.,  150.)
elif(nPeaks == 2):
  FitModel = PythonTools.GetTwoGausFitModel("TwoGausFit", PixValHisto, 0.,  100., 250., 250.)
else:
  print "\tUmm...  I don't quite understand what fit model we're using here..."
  exit()
PixValHisto.Fit(FitModel, "LLEM")
if(nPeaks == 1):
  FitComponents = PythonTools.GetOneGausFitComponents(FitModel)
elif(nPeaks == 2):
  FitComponents = PythonTools.GetTwoGausFitComponents(FitModel)
for fitcomp in FitComponents:
  fitcomp.Draw("same")
aCanvas.Update()

# Pull in the goodness of fit information and the parameter values, then put it in an annotation
# to report it.
thisChi2 = FitModel.GetChisquare()
thisNDF  = FitModel.GetNDF()
thisPVal = FitModel.GetProb()
if(nPeaks == 1):
  Mean = FitModel.GetParameter(2)
  MeEr = FitModel.GetParError(2)
  Sigm = FitModel.GetParameter(3)
  SiEr = FitModel.GetParError(3)  
elif(nPeaks == 2):
  LoMean = FitModel.GetParameter(2)
  LoMeEr = FitModel.GetParError(2)
  LoSigm = FitModel.GetParameter(3)
  LoSiEr = FitModel.GetParError(3)
  HiMean = FitModel.GetParameter(5)
  HiMeEr = FitModel.GetParError(5)
  HiSigm = FitModel.GetParameter(6)
  HiSiEr = FitModel.GetParError(6)
if VerboseProcessing: 
  print "\n\tChi squared per degree of freedom: " + "{:6.1f}".format(thisChi2) + " / " + "{:3.0f}".format(thisNDF) + " = " + "{:3.2f}".format(thisChi2 / thisNDF) + " (p-val = " + "{:2.6f}".format(thisPVal) + ")."
  if(nPeaks == 1):
    print "\tPeak mean  = "  + "{:6.2f}".format(Mean) + " +/- " + "{:2.2f}".format(MeEr) + " ADC Counts."
    print "\tPeak sigma =  " + "{:6.2f}".format(Sigm) + " +/- " + "{:2.2f}".format(SiEr) + " ADC Counts."
  elif(nPeaks == 2):
    print "\t Low peak mean  = "  + "{:6.2f}".format(LoMean) + " +/- " + "{:2.2f}".format(LoMeEr) + " ADC Counts."
    print "\t Low peak sigma =  " + "{:6.2f}".format(LoSigm) + " +/- " + "{:2.2f}".format(LoSiEr) + " ADC Counts."
    print "\tHigh peak mean  = "  + "{:6.2f}".format(HiMean) + " +/- " + "{:2.2f}".format(HiMeEr) + " ADC Counts."
    print "\tHigh peak signa =  " + "{:6.2f}".format(HiSigm) + " +/- " + "{:2.2f}".format(HiSiEr) + " ADC Counts."
if(nPeaks == 1):
  AnnotationHeight = 0.3
elif(nPeaks == 2):
  AnnotationHeight = 0.4
AnnotationLeft  = 0.687
AnnotationRight = 0.987
AnnotationTop   = 0.915
AnnotationBottom = AnnotationTop - AnnotationHeight
thisAnnotation = ROOT.TPaveText(AnnotationLeft,AnnotationBottom,AnnotationRight,AnnotationTop,"blNDC")
thisAnnotation.SetName("SPEAnnotationText")
thisAnnotation.SetBorderSize(1)
thisAnnotation.SetFillColor(ROOT.kWhite)
ThisLine = "#chi^{2} per DoF = " + "{:6.1f}".format(thisChi2) + " / " + str(thisNDF) + " = " + "{:6.2f}".format(thisChi2 / float(thisNDF))
thisAnnotation.AddText(ThisLine)
ThisLine = "(Probability = " + "{:2.6f}".format(thisPVal) + ")"
thisAnnotation.AddText(ThisLine)
if(nPeaks == 1):
  ThisLine = "Mean = "    + "{:6.2f}".format(Mean) + " #pm " + "{:1.2f}".format(MeEr)
  thisAnnotation.AddText(ThisLine)
  ThisLine = "Sigma =  "  + "{:6.2f}".format(Sigm) + " #pm " + "{:1.2f}".format(SiEr)
  thisAnnotation.AddText(ThisLine)
elif(nPeaks == 2):
  ThisLine = "Low Mean = "    + "{:6.2f}".format(LoMean) + " #pm " + "{:1.2f}".format(LoMeEr)
  thisAnnotation.AddText(ThisLine)
  ThisLine = "Low Sigma =  "  + "{:6.2f}".format(LoSigm) + " #pm " + "{:1.2f}".format(LoSiEr)
  thisAnnotation.AddText(ThisLine)
  ThisLine = "High Mean = "   + "{:6.2f}".format(HiMean) + " #pm " + "{:1.2f}".format(HiMeEr)
  thisAnnotation.AddText(ThisLine)
  ThisLine = "High Sigma =  " + "{:6.2f}".format(HiSigm) + " #pm " + "{:1.2f}".format(HiSiEr)
  thisAnnotation.AddText(ThisLine)

# Quick!  Calculate the overal FWHM and throw that in too!
MaxVal = PixValHisto.GetMaximum()
MaxBin = PixValHisto.GetMaximumBin()
LowBin = MaxBin
while(PixValHisto.GetBinContent(LowBin) > (0.5 * MaxVal)):
  LowBin -= 1
LoHalfMax = PixValHisto.GetBinCenter(LowBin)
HighBin = MaxBin
while(PixValHisto.GetBinContent(HighBin) > (0.5 * MaxVal)):
  HighBin += 1
HiHalfMax = PixValHisto.GetBinCenter(HighBin)
FWHM = HiHalfMax - LoHalfMax
ThisLine = "FWHM from Data =  " + "{:6.2f}".format(FWHM)
thisAnnotation.AddText(ThisLine)
thisAnnotation.Draw()

# Save the figure we just made as a pdf and close the input root file.
aCanvas.Update()
aCanvas.SaveAs(InputFilePath.replace(".root", "." + FitModel.GetName() + ".pdf"))
InputFile.Close()

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
