#!/usr/bin/python

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

if(len(sys.argv) != 2):
	print "Usage: python PixValFit.py path/to/fits/root/file"
	exit()

# Pull in the path to the root file we're going to look at
InputFilePath = sys.argv[1]
if(VerboseProcessing): 
	print "\tReading in: '" + InputFilePath + "' for analysis."

# Crack it open, get the pixel value histogram, and zoom in on the interesting part...
InputFile = ROOT.TFile(InputFilePath)
PixValHisto = InputFile.Get("PixValHisto")
PixValHisto.SetLineColor(ROOT.kBlack)
PixValHisto.GetXaxis().SetRangeUser(5900., 8900.)
PixValHisto.GetYaxis().SetTitleOffset(1.2)
# Go ahead and plot this thing now...
aCanvas, aPad = RootPlotLibs.GetReadyToPlot()
aCanvas.Draw()
aCanvas.cd()
aPad.SetLeftMargin(0.08)
aPad.SetRightMargin(0.01)
aPad.SetBottomMargin(0.08)
aPad.Draw()
aPad.cd()
PixValHisto.Draw()

# Create a double-Gaussian fit model, do the fit, and plot the components separately.
#                                     Name    TH1 for range  mean  sigma  mean   sigma 
FitModel = PythonTools.GetFitModel("FitModel", PixValHisto, 6650.,  200., 7100., 300., 7800.,  400.)
PixValHisto.Fit(FitModel, "LLEM")
FitComponents = PythonTools.GetFitComponents(FitModel)
for fitcomp in FitComponents:
  fitcomp.Draw("same")
aCanvas.Update()

# Pull in the goodness of fit information and the parameter values, then put it in an annotation
# to report it.
thisChi2 = FitModel.GetChisquare()
thisNDF  = FitModel.GetNDF()
thisPVal = FitModel.GetProb()
LoMean = FitModel.GetParameter(2)
LoMeEr = FitModel.GetParError(2)
LoSigm = FitModel.GetParameter(3)
LoSiEr = FitModel.GetParError(3)
MiMean = FitModel.GetParameter(5)
MiMeEr = FitModel.GetParError(5)
MiSigm = FitModel.GetParameter(6)
MiSiEr = FitModel.GetParError(6)
HiMean = FitModel.GetParameter(8)
HiMeEr = FitModel.GetParError(8)
HiSigm = FitModel.GetParameter(9)
HiSiEr = FitModel.GetParError(9)
if VerboseProcessing: 
  print "\n\tChi squared per degree of freedom: " + "{:6.1f}".format(thisChi2) + " / " + "{:3.0f}".format(thisNDF) + " = " + "{:3.2f}".format(thisChi2 / thisNDF) + " (p-val = " + "{:2.6f}".format(thisPVal) + ")."
  print "\t Low peak mean  = "  + "{:6.2f}".format(LoMean) + " +/- " + "{:1.2f}".format(LoMeEr) + " ADC Counts."
  print "\t Low peak signa =  " + "{:6.2f}".format(LoSigm) + " +/- " + "{:1.2f}".format(LoSiEr) + " ADC Counts."
  print "\t Mid peak mean  = "  + "{:6.2f}".format(MiMean) + " +/- " + "{:1.2f}".format(MiMeEr) + " ADC Counts."
  print "\t Mid peak signa =  " + "{:6.2f}".format(MiSigm) + " +/- " + "{:1.2f}".format(MiSiEr) + " ADC Counts."
  print "\tHigh peak mean  = "  + "{:6.2f}".format(HiMean) + " +/- " + "{:1.2f}".format(HiMeEr) + " ADC Counts."
  print "\tHigh peak signa =  " + "{:6.2f}".format(HiSigm) + " +/- " + "{:1.2f}".format(HiSiEr) + " ADC Counts."
thisAnnotation = ROOT.TPaveText(0.65,0.50,0.987,0.915,"blNDC")
thisAnnotation.SetName("SPEAnnotationText")
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
ThisLine = "Mid Mean = "   + "{:6.2f}".format(MiMean) + " #pm " + "{:1.2f}".format(MiMeEr)
thisAnnotation.AddText(ThisLine)
ThisLine = "Mid Sigma =  " + "{:6.2f}".format(MiSigm) + " #pm " + "{:1.2f}".format(MiSiEr)
thisAnnotation.AddText(ThisLine)
ThisLine = "High Mean = "   + "{:6.2f}".format(HiMean) + " #pm " + "{:1.2f}".format(HiMeEr)
thisAnnotation.AddText(ThisLine)
ThisLine = "High Sigma =  " + "{:6.2f}".format(HiSigm) + " #pm " + "{:1.2f}".format(HiSiEr)
thisAnnotation.AddText(ThisLine)
thisAnnotation.Draw()

# Save the figure we just made as a pdf and close the input root file.
aCanvas.SaveAs(InputFilePath.replace(".root", ".PixValFit.pdf"))
InputFile.Close()

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()
