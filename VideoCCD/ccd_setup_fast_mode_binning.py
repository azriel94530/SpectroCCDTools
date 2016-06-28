# python script to setup default settings of the fast data taking mode of the SpectroCCD controller 
# make sure idle mode is ON, to ensure the desired state of the shutter
# (soft ARM version)
# Azriel Goldschmidt Jun-16-2016

# need still to add error handling (and remove print outputs)
# desired behaviour is passing error conditions to calling shell script

import urllib
import urllib2
import urlparse
import time
from datetime import datetime
import os
import sys

# if(len(sys.argv) != 2):
#  print "Usage: python Default_Directory "
#  exit()
# 
# 
# DirectoryPath = sys.argv[1]

binning = int(sys.argv[2])

controller_ip = "http://192.168.1.10/"

# prepare the message for setting the timing configuration values

samples_signal = "&dlya=512"
samples_reset = "&dlyb=512"

settling_delay_signal = "&dlyc=10"
settling_delay_reset = "&dlyd=10"
serial_delay = "&dlye=10"
summing_well_delay = "&dlyf=10"
reset_delay = "&dlyg=10"
parallel_delay = "&dlyh=4800"
delay_1 = "&dlyi=10"
delay_2 = "&dlyj=7"
delay_3 = "&dlyk=7"
delay_4 = "&dlyl=7"
pixels_x = "&pixelX=1448"

pixels_y = "&pixelY="+str(int(1440/binning))
print pixels_y

# clear column field now is used to pass the binning
# the least significat bit is removed by the controller
# so a value of 20 is binning of 10 pixles into one vertically
binning_clrcol_field = str(binning*2)
clear_columns ="&clrcol="+binning_clrcol_field

averaging_bits = "&averaging=9"

digital_offset = "&digoff=1000"
exposure_time = "&exptim=5000"
config_ok = "&config=OK"

params = samples_signal + samples_reset +settling_delay_signal + settling_delay_reset + serial_delay +\
summing_well_delay + reset_delay + parallel_delay + delay_1 + delay_2 + delay_3 + delay_4 + pixels_x + pixels_y +\
clear_columns + averaging_bits + digital_offset + exposure_time + config_ok

# print "Parameters:", params

# print "Set the timing configuration values"
response = urllib2.urlopen(controller_ip + "cmd/timing", params)



H1a_enable = "&enChB=on"
H2a_enable = "&enChC=on"
H3a_enable = "&enChD=on"

RGa_enable = "&enChA=on"
SWa_enable = "&enChI=on"

H1b_enable = "&enChF=on"
H2b_enable = "&enChG=on"
H3b_enable = "&enChH=on"

RGb_enable = "&enChE=on"
SWb_enable = "&enChJ=on"

FS1_enable = "&enChM=on"
FS2_enable = "&enChN=on"
FS3_enable = "&enChO=on"
# FS4_enable = "&enChP=off"

V1_enable = "&enChQ=on"
V2_enable = "&enChR=on"
V3_enable = "&enChS=on"
# V4_enable = "&enChT=off"

TGa_enable = "&enChK=on"
TGb_enable = "&enChL=on"

Vsub_enable = "&enChU=on"

Ch1_enable = "&enCh1=on"
Ch2_enable = "&enCh2=on"
Ch3_enable = "&enCh3=on"
Ch4_enable = "&enCh4=on"

On_Off = "&onoff=Enable"

params = H1a_enable + H2a_enable + H3a_enable + RGa_enable + SWa_enable +\
H1b_enable + H2b_enable + H3b_enable + RGb_enable + SWb_enable +\
FS1_enable + FS2_enable + FS3_enable +\
V1_enable + V2_enable + V3_enable +\
TGa_enable + TGb_enable +\
Vsub_enable +\
Ch1_enable + Ch2_enable + Ch3_enable + Ch4_enable + \
On_Off

# print "Parameters:", params

# print "Setting switches (Verticals should be enabled)"
response = urllib2.urlopen(controller_ip + "cmd/enable", params)

# set Idle mode and make sure it is idling
response = urllib2.urlopen(controller_ip + "cmd/idle", params)
html = response.read()
if "Idlemode" in html:
	if "Off" in html:
		response = urllib2.urlopen(controller_ip + "cmd/idle", params)
		html = response.read()
		if "Idlemode" in html and not "Off" in html:
			print "Success settting Idle mode in second toggle"
		else:
			print "Failed to set Idlemode on"
	else:
		print "Succeeded setting Idle mode on first time"
		
else:
	print "Problem setting Idle mode"




