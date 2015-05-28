#!/usr/bin/python

####################################################################################################
# Here are a bunch of functions that read out useful quantities from the LakeShore box we have     #
# running the temperature sensor in the SpectroCCD cryostat.                                       #
####################################################################################################

# Header, import statements etc.
import sys
import string
import time
import socket
import datetime

# Read in the current temperature from the LakeShoreBox through the socket passed to this function
# as an argument.
def ReadCurrentTemp(lakeshoresocket):
  # Set the wait time between commands.
  WaitTime = 0.1 #[s]
  # Clear Communications
  lakeshoresocket.sendall('*CLS\r\n')
  time.sleep(WaitTime)
  # Set Controller to Remote Mode
  lakeshoresocket.sendall('MODE 1\r\n')
  time.sleep(WaitTime)
  # First Read is a throw-away, so just readback the mode
  lakeshoresocket.sendall('MODE?\r\n')
  time.sleep(WaitTime)
  thisBuffer = lakeshoresocket.recv(16)
  # Actually read in the temperature.
  lakeshoresocket.sendall('CRDG? B\r\n')
  time.sleep(WaitTime)
  thisTime = lakeshoresocket.recv(16)
  readableTime = float(str(thisTime[0] + thisTime[1] + thisTime[2] + thisTime[3] + thisTime[4] + thisTime[5]).replace("+", ""))
  # Return the value we just read and call it a day.
  return readableTime

# Read in the temperature set point from the LakeShoreBox through the socket passed to this 
# function as an argument.
def ReadTempSetPoint(lakeshoresocket):
  # Set the wait time between commands.
  WaitTime = 0.1 #[s]
  # Clear Communications
  lakeshoresocket.sendall('*CLS\r\n')
  time.sleep(WaitTime)
  # Set Controller to Remote Mode
  lakeshoresocket.sendall('MODE 1\r\n')
  time.sleep(WaitTime)
  # First Read is a throw-away, so just readback the mode
  lakeshoresocket.sendall('MODE?\r\n')
  time.sleep(WaitTime)
  thisBuffer = lakeshoresocket.recv(16)
  # Actually read in the temperature set point.
  lakeshoresocket.sendall('SETP? 1\r\n')
  time.sleep(WaitTime)
  thisSetPoint = lakeshoresocket.recv(16)
  readableSetPoint = float(str(thisSetPoint[0] + thisSetPoint[1] + thisSetPoint[2] + thisSetPoint[3] + thisSetPoint[4] + thisSetPoint[5]).replace("+", ""))
  # Return the value we just read and call it a day.
  return readableSetPoint

# Read in the heater power level from the LakeShoreBox through the socket passed to this function
# as an argument.
def ReadHeaterLevel(lakeshoresocket):
  # Set the wait time between commands.
  WaitTime = 0.1 #[s]
  # Clear Communications
  lakeshoresocket.sendall('*CLS\r\n')
  time.sleep(WaitTime)
  # Set Controller to Remote Mode
  lakeshoresocket.sendall('MODE 1\r\n')
  time.sleep(WaitTime)
  # First Read is a throw-away, so just readback the mode
  lakeshoresocket.sendall('MODE?\r\n')
  time.sleep(WaitTime)
  thisBuffer = lakeshoresocket.recv(16)
  # Actually read in the heater level.
  lakeshoresocket.sendall('HTR? 1\r\n')
  time.sleep(WaitTime)
  thisHeaterLevel = lakeshoresocket.recv(16)
  readableHeaterLevel = float(str(thisHeaterLevel[0] + thisHeaterLevel[1] + thisHeaterLevel[2] + thisHeaterLevel[3] + thisHeaterLevel[4] + thisHeaterLevel[5]).replace("+", ""))
  # Return the value we just read and call it a day.
  return readableHeaterLevel

# Read in the heater state from the LakeShoreBox through the socket passed to this function as an 
# argument.
def ReadHeaterState(lakeshoresocket):
  # Set the wait time between commands.
  WaitTime = 0.1 #[s]
  # Clear Communications
  lakeshoresocket.sendall('*CLS\r\n')
  time.sleep(WaitTime)
  # Set Controller to Remote Mode
  lakeshoresocket.sendall('MODE 1\r\n')
  time.sleep(WaitTime)
  # First Read is a throw-away, so just readback the mode
  lakeshoresocket.sendall('MODE?\r\n')
  time.sleep(WaitTime)
  thisBuffer = lakeshoresocket.recv(16)
  # Actually read in the heater state.
  lakeshoresocket.sendall('RANGE? 1\r\n')
  time.sleep(WaitTime)
  thisHeaterState = int(lakeshoresocket.recv(16))
  if(thisHeaterState == 0):  HeaterStateString = "OFF"
  elif thisHeaterState == 1: HeaterStateString = "LOW POWER"
  elif thisHeaterState == 2: HeaterStateString = "HIGH POWER"
  else: HeaterStateString = "Value Out of Range!!!"
  # Return the value we just read and call it a day.
  return HeaterStateString

