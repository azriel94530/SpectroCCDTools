#!/usr/bin/python

####################################################################################################
# Read out the temperature on the SpectroCCD board from the LakeShore box (we're using a 325 right #
# now, but I'm not sure that really matters...).  For now, it's just going to write to the screen  #
# and a text file until we get a kill signal, but eventually it would be nice to push this to some #
# kind of SQL-ish database or the like.                                                            #
####################################################################################################

# Header, import statements etc.
import sys
import string
import time
import socket
import datetime
import LakeShoreTools

####################################
#  BEGIN MAIN BODY OF THE CODE!!!  #
####################################

# Check for the correct ussage.
if(len(sys.argv) != 4):
  print "Usage: python ReadTempFromLakeshore.py /path/to/output/text/file RunTimeInSeconds SamplingTimeInSeconds"
  exit()

# Set some flags for how verbose our input and output are going to be.
Debugging = False
VerboseProcessing = True

# Set the IP address and port of the LakeShore box.
LS325_IP   = "192.168.1.46"
LS325_PORT = 9001

# Create a socket and connect.
LS325Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LS325Socket.settimeout(3)
LS325Socket.connect((LS325_IP,LS325_PORT))

# Open the output text file.
OutputFile = open(sys.argv[1], 'w')

# Construct the start time and print out the header.
StartTime = time.time()
StartTimeString = datetime.datetime.fromtimestamp(StartTime).strftime('%Y-%m-%d %H:%M:%S')

# Set the stop time and sampling period rom the second argument.
StopTime = StartTime + float(sys.argv[2])
StopTimeString = datetime.datetime.fromtimestamp(StopTime).strftime('%Y-%m-%d %H:%M:%S')
SamplingTime = float(sys.argv[3])
if(VerboseProcessing): print "\tSampling every", SamplingTime, "seconds, from", StartTimeString, "to", StopTimeString + "."

# Start the timey-wimey loop!
while(time.time() < StopTime):
  # Get the current time.
  thisTime = time.time()
  thisTimeString = datetime.datetime.fromtimestamp(thisTime).strftime('%Y-%m-%d %H:%M:%S')
  # Print out the header.
  if(VerboseProcessing): print "CD Temperature Monitor at " + thisTimeString
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
  # Now, wait for the sampling time, so that we don't just go nuts on this...
  time.sleep(SamplingTime)

# Be nice and close the socket and the text file now that we're done with it.
LS325Socket.close()
OutputFile.close()

# OK, we're done!
exit()

