# python script to setup default settings of the slow data taking mode of the SpectroCCD controller 
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


H1a_enable = "enChB=on"
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




