# python script to upload a timing file to controller (needed for shutter control through idle sequence) 
# (soft ARM version)
# Azriel Goldschmidt Jun-16-2016

# need still to add error handling (and remove print outputs)
# desired behaviour is passing error conditions to calling shell script

import requests
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

files = {'BRAM_File': open('../TimingFiles/Timing_06222016.txt')}

# f = open('../TimingFiles/Timing_06222016.txt','r')

#headers = {'Content-Type': 'text/plain'}

r = requests.post(controller_ip+"cmd/FILExhrBRAM", files=files)

#r = requests.post(controller_ip+"cmd/FILExhrBRAM", files=files, headers=headers)
#r = requests.post(controller_ip+"timing.txt", files=files, headers=headers)

#r = requests.post(controller_ip+"timing.txt", files=files, headers=headers)

# f = open('../TimingFiles/Timing_06222016.txt','r')


# print datagen

# print headers

# print params

# print "Uploading timing file"
# params=f.read()
# response = urllib2.urlopen(controller_ip + "timing.txt", params)

