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

# binning = int(sys.argv[2])
binning = 1

controller_ip = "http://192.168.1.10/"

params = ""
# Turn power on (analog power on the controller)
response = urllib2.urlopen(controller_ip + "cmd/power1", params)
print "Response from Analog Power On: "+response.read()

time.sleep(1)

VDD1 = "dac_17=-30"
VDD2 = "&dac_18=-30"
VDD3 = "&dac_19=-30"
VDD4 = "&dac_20=-30"

RESET1 = "&dac_09=-15.5"
RESET2 = "&dac_10=-15.5"
RESET3 = "&dac_11=-15.5"
RESET4 = "&dac_12=-15.5"

OUTPUT_GATE1 = "&dac_13=-1.0"
OUTPUT_GATE2 = "&dac_14=-1.0"
OUTPUT_GATE3 = "&dac_15=-1.0"
# different due to esd damage
OUTPUT_GATE4 = "&dac_16=1.5"

PGA1 = "&dac_01=-0.37"
PGA2 = "&dac_02=-0.33"
PGA3 = "&dac_03=-0.18"
PGA4 = "&dac_04=-0.19"

CONV_OFFSET1 = "&dac_05=2"
CONV_OFFSET2 = "&dac_06=2"
CONV_OFFSET3 = "&dac_07=2"
CONV_OFFSET4 = "&dac_08=2"

PGA_GAIN = "&pga_g=4"

params =\
VDD1+VDD2+VDD3+VDD4+\
RESET1+RESET2+RESET3+RESET4+\
OUTPUT_GATE1+OUTPUT_GATE2+OUTPUT_GATE3+OUTPUT_GATE4+\
PGA1+PGA2+PGA3+PGA4+\
CONV_OFFSET1+CONV_OFFSET2+CONV_OFFSET3+CONV_OFFSET4+\
PGA_GAIN

# print "Parameters:", params

# print "Set the timing configuration values"
response = urllib2.urlopen(controller_ip + "cmd/dacxhr", params)
print "Response from Video Voltage Configuration: "+response.read()

timing_file  = "Timing_binning.txt"

# print "Uploading timing file that idles with shutter open"

f = open('../TimingFiles/'+timing_file,'r')
timing_file_content=f.read()
content_length = str(len(timing_file_content))+"\r"

message = '-----Content-Length: ' + content_length + 'filename="' +timing_file+'" Content-Type: text/plain'+'....'+timing_file_content+'-----'

response = urllib2.urlopen(controller_ip + "cmd/FILExhrBRAM", message)
print "Response to Upload of default timing file"+response.read()

# prepare the message for setting the timing configuration values

samples_signal = "&dlya=64"
samples_reset = "&dlyb=64"
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

# clear column field now is used to pass the binning
# the least significat bit is removed by the controller
# so a value of 20 is binning of 10 pixles into one vertically
binning_clrcol_field = str(binning*2)
clear_columns ="&clrcol="+binning_clrcol_field

averaging_bits = "&averaging=6"
digital_offset = "&digoff=1000"
exposure_time = "&exptim=5000"
config_ok = "&config=OK"

params = samples_signal + samples_reset +settling_delay_signal + settling_delay_reset + serial_delay +\
summing_well_delay + reset_delay + parallel_delay + delay_1 + delay_2 + delay_3 + delay_4 + pixels_x + pixels_y +\
clear_columns + averaging_bits + digital_offset + exposure_time + config_ok

# print "Parameters:", params

# print "Set the timing configuration values"
response = urllib2.urlopen(controller_ip + "cmd/timing", params)
print "Response from Timing Configuration: "+response.read()

# prepare the message for setting the timing configuration values
SCLK1a_L = "dac_05=-5"
SCLK2a_L = "&dac_03=-5"
SCLK3a_L = "&dac_01=-5"
RG1_L    = "&dac_07=-1"
SW1_L    = "&dac_39=-8"
SCLK1b_L = "&dac_13=-5"
SCLK2b_L = "&dac_11=-5"
SCLK3b_L = "&dac_09=-5"
RG2_L    = "&dac_15=-1"
SW2_L    = "&dac_37=-8"
SCLK1a_H = "&dac_06=5"
SCLK2a_H = "&dac_04=5"
SCLK3a_H = "&dac_02=5"
RG1_H    = "&dac_08=-7"
SW1_H    = "&dac_40=2"
SCLK1b_H = "&dac_14=5"
SCLK2b_H = "&dac_12=5"
SCLK3b_H = "&dac_10=5"
RG2_H    = "&dac_16=-7"
SW2_H    = "&dac_38=2"
FS1_L    = "&dac_31=-5"
FS2_L    = "&dac_29=-5"
FS3_L    = "&dac_27=-5"
FS4_L    = "&dac_25=0"
V1_L     = "&dac_23=-5"
V2_L     = "&dac_21=-5"
V3_L     = "&dac_19=-5"
V4_L     = "&dac_17=0"
TG1_L    = "&dac_35=-5"
TG2_L    = "&dac_33=-5"
FS1_H    = "&dac_32=5"
FS2_H    = "&dac_30=5"
FS3_H    = "&dac_28=5"
FS4_H    = "&dac_26=0"
V1_H     = "&dac_24=5"
V2_H     = "&dac_22=5"
V3_H     = "&dac_20=5"
V4_H     = "&dac_18=0"
TG1_H    = "&dac_36=5"
TG2_H    = "&dac_34=5"
VSUB     = "&dac_41=100"
ERASE_VCK= "&erase1=9"
ERASE_VSB= "&erase2=0"
ERASE_SLW= "&erase3=100"
ERASE_TIM= "&erase4=0.5"
EPURG_VCK= "&erase5=-9"
EPURG_TIM= "&erase6=0.5"

params =\
SCLK1a_L+SCLK2a_L+SCLK3a_L+RG1_L+SW1_L+SCLK1b_L+SCLK2b_L+SCLK3b_L+RG2_L+SW2_L+\
SCLK1a_H+SCLK2a_H+SCLK3a_H+RG1_H+SW1_H+SCLK1b_H+SCLK2b_H+SCLK3b_H+RG2_H+SW2_H+\
FS1_L+FS2_L+FS3_L+FS4_L+V1_L+V2_L+V3_L+V4_L+TG1_L+TG2_L+\
FS1_H+FS2_H+FS3_H+FS4_H+V1_H+V2_H+V3_H+V4_H+TG1_H+TG2_H+\
VSUB+ERASE_VCK+ERASE_VSB+ERASE_SLW+ERASE_TIM+EPURG_VCK+EPURG_TIM

# print "Parameters:", params

# print "Set the timing configuration values"
response = urllib2.urlopen(controller_ip + "cmd/clkdac", params)
print "Response from Clock Voltages Configuration: "+response.read()


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

# print "Setting switches (Verticals should be enabled)"
response = urllib2.urlopen(controller_ip + "cmd/enable", params)
print "Enable response: "+response.read()


# set Idle mode and make sure it is idling
response = urllib2.urlopen(controller_ip + "cmd/idle", params)
html = response.read()
# print html
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




