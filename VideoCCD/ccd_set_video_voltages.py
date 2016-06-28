# python script to set all the video voltages
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

print "Parameters:", params

# print "Set the timing configuration values"
response = urllib2.urlopen(controller_ip + "cmd/dacxhr", params)
print response.read()




