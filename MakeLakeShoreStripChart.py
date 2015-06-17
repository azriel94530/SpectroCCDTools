#!/usr/bin/python

####################################################################################################
# Read out the temperature on the SpectroCCD board from the LakeShore box (we're using a 325 right #
# now, but I'm not sure that really matters...).  For now, it's just going to write to the screen  #
# and a text file until we get a kill signal, but eventually it would be nice to push this to some #
# kind of SQL-ish database or the like.                                                            #
####################################################################################################

# Header, import statements etc.
import sys
import os
import ROOT
import string
import time
import socket
import datetime
import LakeShoreTools
import RootPlotLibs
import array

####################################
#  BEGIN MAIN BODY OF THE CODE!!!  #
####################################

# Check for the correct ussage.
if(len(sys.argv) != 3):
  print "Usage: python MakeLakeShoreStripChart.py /path/to/output/text/file.txt SamplingTimeInSeconds"
  exit()

# Set some flags for how verbose our input and output are going to be.
Debugging = False
VerboseProcessing = True

# Set the IP address and port of the LakeShore box.
LS325_IP   = "192.168.1.46"
LS325_PORT = 9001

if(VerboseProcessing): print "\tReading in from Lakeshore box at IP:", LS325_IP, "on port:", str(LS325_PORT) + "."

# Set the name of the output file from the first argument and erase it if it exists already.
OutputFileName = sys.argv[1]
if(OutputFileName[-4:] != ".txt"):
  print "Please make sure your output file ends with \'.txt\'"
  exit()
if os.path.exists(OutputFileName):
  print "Removing old version of", OutputFileName
  os.system("rm " + OutputFileName)

# Set the sampling period from the second argument.
SamplingTime = float(sys.argv[2])
if(SamplingTime < 10.): SamplingTime = 10.
if(VerboseProcessing): print "\tSampling every", SamplingTime, "seconds."

# Now get ROOT started up so that we can make a plot that updates nicely.
ROOT.gROOT.Reset()
ROOT.gStyle.SetOptTitle(0)
aCanvas = RootPlotLibs.A720pCanvas()
aCanvas.Draw()
aCanvas.cd()
aPad = RootPlotLibs.ASimplePad()
aPad.SetTopMargin(0.02)
aPad.SetLeftMargin(0.1)
aPad.SetBottomMargin(0.04)
aPad.SetRightMargin(0.02)
aPad.Draw()
aPad.cd()

# Python lists to hold the time and temperature data...
TimeData = []
TempData = []

# Start the infinite timey-wimey loop!
while(True):
  # Create a socket and connect.
  LS325Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  LS325Socket.settimeout(3)
  LS325Socket.connect((LS325_IP, LS325_PORT))
  # Actually open the output text file.
  OutputFile = open(OutputFileName, 'a')
  # Get the current time.
  thisTime = time.time()
  thisTimeString = datetime.datetime.fromtimestamp(thisTime).strftime('%Y-%m-%d %H:%M:%S')
  # Print out the header.
  if(VerboseProcessing): print "CCD Temperature Monitor at " + thisTimeString
  # Read in the information we want through this socket.
  thisTemperature = LakeShoreTools.ReadCurrentTemp(LS325Socket)
  if(Debugging): print thisTemperature
  thisTempSetPoint = LakeShoreTools.ReadTempSetPoint(LS325Socket)
  if(Debugging): print thisTempSetPoint
  thisHeaterLevel = LakeShoreTools.ReadHeaterLevel(LS325Socket)
  if(Debugging): print thisHeaterLevel
  thisHeaterState = LakeShoreTools.ReadHeaterState(LS325Socket)
  if(Debugging): print thisHeaterState
  # Print out results...
  if(VerboseProcessing): 
    print "\t   Temperature:", thisTemperature,  "C"
    print "\tTemp Set Point:", thisTempSetPoint, "C"
    print "\t  Heater Level:", str(thisHeaterLevel) + "%"
    print "\t  Heater State:", thisHeaterState
  # Write the temperature data to the text file
  OutputFile.write(thisTimeString + "\t" + str(thisTemperature) + "\t" + str(thisTempSetPoint) + "\t" + str(thisHeaterLevel) + "\t" + thisHeaterState + "\n")
  # Append the time and temperature to the python lists we made for them
  #TimeData.append(thisTime)
  #TimeData.append(datetime.datetime.fromtimestamp(thisTime).strftime('%Y-%m-%d %H:%M:%S'))
  TimeData.append(datetime.datetime.fromtimestamp(thisTime))
  TempData.append(thisTemperature)
  PlotTime = []
  for thisTime in TimeData:
    ElapsedTime = thisTime - TimeData[0]
    #print ElapsedTime.total_seconds() / 60.
    PlotTime.append(ElapsedTime.total_seconds())  
    #PlotTime.append(ElapsedTime)
  PlotTime = array.array("f", PlotTime)
  PlotTemp = array.array("f", TempData)
  CoolDownGraph = ROOT.TGraph(len(PlotTime), PlotTime, PlotTemp)
  CoolDownGraph.GetXaxis().SetTimeDisplay(1)
  TimeOffset = ROOT.TDatime(TimeData[0].year, TimeData[0].month, TimeData[0].day, TimeData[0].hour, TimeData[0].minute, TimeData[0].second)
  CoolDownGraph.GetXaxis().SetTimeOffset(TimeOffset.Convert())
  CoolDownGraph.GetXaxis().SetTimeFormat("%H:%M")
  CoolDownGraph.GetXaxis().SetLabelSize(0.03)
  CoolDownGraph.GetYaxis().SetTitle("Temperature [C]")
  CoolDownGraph.GetYaxis().SetTitleSize(0.05)
  CoolDownGraph.GetYaxis().SetTitleOffset(1.0)
  CoolDownGraph.GetYaxis().SetLabelSize(0.03)
  CoolDownGraph.Draw("al")
  aCanvas.Update()
  aCanvas.SaveAs(sys.argv[1].replace("txt", "pdf"))
  # Be nice and close the socket and the text file now that we're done with it.
  LS325Socket.close()
  OutputFile.close()
  # Now, wait for the sampling time, so that we don't just go nuts on this...
  time.sleep(SamplingTime)
  del CoolDownGraph

# OK, we should never actually get to this, but let's put an exit() at the end just for good form...
exit()

