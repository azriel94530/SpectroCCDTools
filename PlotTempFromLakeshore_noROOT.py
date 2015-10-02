#!/usr/bin/python

####################################################################################################
# Open up a file of the temperature data dumped to a file by the python script on the SpectroCCD   #
# computer and a nice plot of it.                                                                  #
####################################################################################################

# Header, import statements etc.
import sys
import time
import datetime
import matplotlib.pyplot as plt

####################################
#  BEGIN MAIN BODY OF THE CODE!!!  #
####################################

# Get the start time of this calculation
StartTime = time.time()

# Set some flags for how verbose our input and output are going to be.
Debugging = False
VerboseProcessing = True

if(len(sys.argv) != 2):
  print "Usage: python ReadTemps.py path/to/temperature/log/file"
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

# Put together the plot.
plt.figure(figsize=(7, 4))
plt.plot(TimeData, TempData, linestyle='-', linewidth=2)

# Make the plot look nice.
plt.xlabel('Time')
plt.ylabel('Temperature [C]')
plt.gcf().autofmt_xdate()
plt.grid(b=True, which='major', color='k', linestyle='--')

# Show the plot for a while and then save it to a pdf.
plt.tight_layout()
plt.ion()
plt.show()
time.sleep(5.)
plt.savefig(sys.argv[1].replace("txt", "pdf"))
#raw_input()

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for this code to run."
exit()

