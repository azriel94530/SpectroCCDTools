#!/usr/bin/python

####################################################################################################
# Read out the temperature from John's temperature sensor box, and make a nice auto-updating plot  #
# of it as a function of time.  Once started, this will just keep going until it get's a kill      #
# signal.                                                                                          #
####################################################################################################

# Header, import statements etc.
import sys
import os
import string
import time
import socket
import datetime
import matplotlib.pyplot as plt

def CalculateTemperature(rawsetpoint, rawtempval):
  # First the set point...
  NormalizedSetPoint = float(rawsetpoint) / 0.01
  Eq1 = -242.02 + (2.2228 * NormalizedSetPoint)
  Eq2 = 0.0025859 * (NormalizedSetPoint**2)
  Eq3 = -0.0000048260 * (NormalizedSetPoint**3)
  Eq4 = -0.000000028183 * (NormalizedSetPoint**4)
  Eq5 = 0.00000000015243 * (NormalizedSetPoint**5)
  SetPointValue = str(Eq1 + Eq2 + Eq3 + Eq4 + Eq5)
  # And the temperature value...
  NormaizedTemperature = float(rawtempval) / 0.01
  Eq1 = -242.02 + (2.2228 * NormaizedTemperature)
  Eq2 = 0.0025859 * (NormaizedTemperature**2)
  Eq3 = -0.0000048260 * (NormaizedTemperature**3)
  Eq4 = -0.000000028183 * (NormaizedTemperature**4)
  Eq5 = 0.00000000015243 * (NormaizedTemperature**5)
  TemperatureValue = str(Eq1 + Eq2 + Eq3 + Eq4 + Eq5)
  # Return the setpoint and temperature
  return SetPointValue, TemperatureValue

####################################
#  BEGIN MAIN BODY OF THE CODE!!!  #
####################################

# Check for the correct ussage.
if(len(sys.argv) != 3):
  print "Usage: python MakeTemperatureStripChart.py /path/to/output/text/file.txt SamplingTimeInSeconds"
  exit()

# Set some flags for how verbose our input and output are going to be.
Debugging = False
VerboseProcessing = True

# Set up the IP address and port, etc.
SCCD_TC_IP   = "192.168.1.20"
SCCD_TC_PORT = 1025
buf=1024
addr=(SCCD_TC_IP, SCCD_TC_PORT)
#print addr
# Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(3)
s.connect(addr)

if(VerboseProcessing): print "\tReading in temperature data from box at IP:", SCCD_TC_IP, "on port:", str(SCCD_TC_PORT) + "."

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

# Python lists to hold the time and temperature data...
TimeData  = []
TempData1 = []
SetPData1 = []
TempData2 = []
SetPData2 = []
TempData3 = []
SetPData3 = []

# Set up the plot...
plt.figure(figsize=(16, 9))
plt.xlabel('Time')
plt.ylabel('Temperature [C]')
plt.gcf().autofmt_xdate()
plt.grid(b=True, which='major', color='k', linestyle=':')
plt.ion()
plt.show()

# Start the infinite timey-wimey loop!
while(True):
  # Pull in the temperature data and set point from the socket we just opened.
  s.sendall('#01\r')
  RawData, RawAddr = s.recvfrom(buf)
  RawSetP1 = RawData[2:8]
  RawTemp1 = RawData[9:15]  
  RawSetP2 = RawData[16:22]
  RawTemp2 = RawData[23:29]
  RawSetP3 = RawData[30:36]
  RawTemp3 = RawData[37:43]
  # Calculate the temperature from the raw data:
  thisSetPointValue1, thisTemperature1 = CalculateTemperature(RawSetP1, RawTemp1)
  thisSetPointValue2, thisTemperature2 = CalculateTemperature(RawSetP2, RawTemp2)
  thisSetPointValue3, thisTemperature3 = CalculateTemperature(RawSetP3, RawTemp3)
  # Actually open the output text file.
  OutputFile = open(OutputFileName, 'a')
  # Get the current time.
  thisTime = time.time()
  thisTimeString = datetime.datetime.fromtimestamp(thisTime).strftime('%Y-%m-%d %H:%M:%S')
  # Print out the header.
  if(VerboseProcessing): print "CCD Temperature Monitor at " + thisTimeString
  # Read in the information we want through this socket.
  # Print out results...
  if(VerboseProcessing): 
    print "\t   Temperature 1:", thisTemperature1,  "C"
    print "\tTemp Set Point 1:", thisSetPointValue1, "C"
    print "\t   Temperature 2:", thisTemperature2,  "C"
    print "\tTemp Set Point 2:", thisSetPointValue2, "C"
    print "\t   Temperature 3:", thisTemperature3,  "C"
    print "\tTemp Set Point 3:", thisSetPointValue3, "C"
  # Write the temperature data to the text file
  OutputFile.write(thisTimeString + "\t" + str(thisTemperature1) + "\t" + str(thisSetPointValue1) + "\t" + str(thisTemperature2) + "\t" + str(thisSetPointValue2) + "\t" + str(thisTemperature3) + "\t" + str(thisSetPointValue3))
  # Append the time and temperature to the python lists we made for them
  TimeData.append(datetime.datetime.fromtimestamp(thisTime))
  TempData1.append(thisTemperature1)
  SetPData1.append(thisSetPointValue1)
  TempData2.append(thisTemperature2)
  SetPData2.append(thisSetPointValue2)
  TempData3.append(thisTemperature3)
  SetPData3.append(thisSetPointValue3)
  # If we have two or more entries in the temperature data, then plot this thing...
  if(len(TempData1) > 1):
    plt.plot(TimeData, TempData1, 'b-',  linewidth=2, label="Temp 1")
    plt.plot(TimeData, SetPData1, 'b--', linewidth=2, label="SetP 1")
    plt.plot(TimeData, TempData2, 'r-',  linewidth=2, label="Temp 2")
    plt.plot(TimeData, SetPData2, 'r--', linewidth=2, label="SetP 2")
    plt.plot(TimeData, TempData3, 'g-',  linewidth=2, label="Temp 3")
    plt.plot(TimeData, SetPData3, 'g--', linewidth=2, label="SetP 3")
    if(len(TempData1) == 2):
      plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=6, mode="expand", borderaxespad=0.)
    plt.draw()
    plt.pause(0.0001)
    # Save the figure to a pdf.
    plt.savefig(sys.argv[1].replace("txt", "pdf"))
  OutputFile.close()
  # Now, wait for the sampling time, so that we don't just go nuts on this, and then clear the plot
  # so that we can make a new one.
  time.sleep(SamplingTime)

# OK, we should never actually get to this, but let's put an exit() at the end just for good form...
exit()

