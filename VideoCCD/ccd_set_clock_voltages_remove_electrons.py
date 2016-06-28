# python script to set all the clock voltages
# this version is to try and sweep the electrons towards the
# shift register area (and hopefully to vsub)
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
SCLK1a_L = "dac_05=11"
SCLK2a_L = "&dac_03=11"
SCLK3a_L = "&dac_01=11"
RG1_L    = "&dac_07=-1"
SW1_L    = "&dac_39=-8"
SCLK1b_L = "&dac_13=11"
SCLK2b_L = "&dac_11=11"
SCLK3b_L = "&dac_09=11"
RG2_L    = "&dac_15=-1"
SW2_L    = "&dac_37=-8"
SCLK1a_H = "&dac_06=11"
SCLK2a_H = "&dac_04=11"
SCLK3a_H = "&dac_02=11"
RG1_H    = "&dac_08=-7"
SW1_H    = "&dac_40=2"
SCLK1b_H = "&dac_14=11"
SCLK2b_H = "&dac_12=11"
SCLK3b_H = "&dac_10=11"
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
TG1_L    = "&dac_35=8"
TG2_L    = "&dac_33=8"
FS1_H    = "&dac_32=5"
FS2_H    = "&dac_30=5"
FS3_H    = "&dac_28=5"
FS4_H    = "&dac_26=0"
V1_H     = "&dac_24=5"
V2_H     = "&dac_22=5"
V3_H     = "&dac_20=5"
V4_H     = "&dac_18=0"
TG1_H    = "&dac_36=8"
TG2_H    = "&dac_34=8"
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

print "Parameters:", params

# print "Set the timing configuration values"
response = urllib2.urlopen(controller_ip + "cmd/clkdac", params)





