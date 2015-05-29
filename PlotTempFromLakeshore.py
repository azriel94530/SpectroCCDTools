#!/usr/bin/python

####################################################################################################
# Open up a file of the temperature data dumped to a file by the python script on the SpectroCCD   #
# computer and a nice plot of it.                                                                  #
####################################################################################################

# Header, import statements etc.
import ROOT
import sys
import time
import datetime
import array
import RootPlotLibs

####################################
#  BEGIN MAIN BODY OF THE CODE!!!  #
####################################

# Reset root because that's totally a thing we do.
ROOT.gROOT.Reset()

# and turn off plot titles for now...
ROOT.gStyle.SetOptTitle(0)

# Get the start time of this calculation
StartTime = time.time()

# Set some flags for how verbose our input and output are going to be.
Debugging = False
VerboseProcessing = True

if(len(sys.argv) != 2):
  print "Usage: python ReadTemps.py path/to/file"
  exit()

# Pull in the path to the text file we're going to look at
InputFilePath = sys.argv[1]
if(VerboseProcessing): 
  print "\tReading in: '" + InputFilePath + "' for analysis."

# Open up the file..
thisFile = open(sys.argv[1], 'rU')

# Python lists to hold the time and temperature data...
TimeData = []
TempData = []

for Row in thisFile:
  if(Debugging): print Row
  # Parse the date and time.
  thisYear   = int(Row.split("\t")[0].split(" ")[0].split("-")[0])
  thisMonth  = int(Row.split("\t")[0].split(" ")[0].split("-")[1])
  thisDay    = int(Row.split("\t")[0].split(" ")[0].split("-")[2])
  thisHour   = int(Row.split("\t")[0].split(" ")[1].split(":")[0])
  thisMinute = int(Row.split("\t")[0].split(" ")[1].split(":")[1])
  thisSecond = int(Row.split("\t")[0].split(" ")[1].split(":")[2])
  thisDate = datetime.datetime(thisYear, thisMonth, thisDay, thisHour, thisMinute, thisSecond)
  TimeData.append(thisDate)
  # Now parse the temperature.
  thisTemp = float(Row.split("\t")[1])
  TempData.append(thisTemp)

# Close up the text file.
thisFile.close()

# Make sure we recorded the same number of points in both time and temperature...
if(len(TimeData) == len(TempData)):
  print "\tRead in", len(TimeData), "points."
else:
  print "\tSomehow, TimeData and TempData ended up with different numbers of points in them..."
  exit()

# Now, let's convert these things into a TGraph object
PlotTime = []
for thisTime in TimeData:
  ElapsedTime = thisTime - TimeData[0]
  #print ElapsedTime.total_seconds() / 60.
  PlotTime.append(ElapsedTime.total_seconds())
PlotTime = array.array("f", PlotTime)
TempData = array.array("f", TempData)
CoolDownGraph = ROOT.TGraph(len(PlotTime), PlotTime, TempData)
CoolDownGraph.GetXaxis().SetTimeDisplay(1)
TimeOffset = ROOT.TDatime(TimeData[0].year, TimeData[0].month, TimeData[0].day, TimeData[0].hour, TimeData[0].minute, TimeData[0].second)
CoolDownGraph.GetXaxis().SetTimeOffset(TimeOffset.Convert())
CoolDownGraph.GetXaxis().SetTimeFormat("%H:%M")
CoolDownGraph.GetXaxis().SetLabelSize(0.03)
CoolDownGraph.GetYaxis().SetTitle("Temperature [C]")
CoolDownGraph.GetYaxis().SetTitleSize(0.05)
CoolDownGraph.GetYaxis().SetTitleOffset(0.8)
CoolDownGraph.GetYaxis().SetLabelSize(0.03)
# Get ready to plot this thing.
aCanvas = RootPlotLibs.ASimpleCanvas()
aCanvas.Draw()
aCanvas.cd()
aPad = RootPlotLibs.ASimplePad()
aPad.SetTopMargin(0.02)
aPad.SetLeftMargin(0.09)
aPad.SetBottomMargin(0.04)
aPad.SetRightMargin(0.02)
aPad.Draw()
aPad.cd()
CoolDownGraph.Draw()
aCanvas.Update()
aCanvas.SaveAs(sys.argv[1].replace("txt", "pdf"))
#raw_input()

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()

