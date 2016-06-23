# python script to setup default settings of the slow data taking mode of the SpectroCCD controller 
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

controller_ip = "http://192.168.1.10/"

# prepare the message for setting the timing configuration values

samples_signal = "&dlya=1024"
samples_reset = "&dlyb=1024"
settling_delay_signal = "&dlyc=40"
settling_delay_reset = "&dlyd=30"
serial_delay = "&dlye=30"
summing_well_delay = "&dlyf=40"
reset_delay = "&dlyg=20"
parallel_delay = "&dlyh=48000"
delay_1 = "&dlyi=10"
delay_2 = "&dlyj=7"
delay_3 = "&dlyk=7"
delay_4 = "&dlyl=7"
pixels_x = "&pixelX=1448"
pixels_y = "&pixelY=1440"
clear_columns ="&clrcol=1000"
averaging_bits = "&averaging=10"
digital_offset = "&digoff=5000"
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

# FS1_enable = "&enChM=off"
# FS2_enable = "&enChN=off"
# FS3_enable = "&enChO=off"
# FS4_enable = "&enChP=off"

# V1_enable = "&enChQ=off"
# V2_enable = "&enChR=off"
# V3_enable = "&enChS=off"
# V4_enable = "&enChT=off"

# TGa_enable = "&enChK=off"
# TGb_enable = "&enChL=off"

Vsub_enable = "&enChU=on"

Ch1_enable = "&enCh1=on"
Ch2_enable = "&enCh2=on"
Ch3_enable = "&enCh3=on"
Ch4_enable = "&enCh4=on"

On_Off = "&onoff=Enable"

params = H1a_enable + H2a_enable + H3a_enable + RGa_enable + SWa_enable +\
H1b_enable + H2b_enable + H3b_enable + RGb_enable + SWb_enable +\
Vsub_enable +\
Ch1_enable + Ch2_enable + Ch3_enable + Ch4_enable + \
On_Off

# FS1_enable + FS2_enable + FS3_enable + FS4_enable +\
# V1_enable + V2_enable + V3_enable + V4_enable +\
# TGa_enable + TGb_enable +\

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



