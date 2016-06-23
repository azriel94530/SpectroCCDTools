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
timing_file  = "Timing_binning_close.txt"

print "Uploading timing file that idles with shutter closed"

f = open('../TimingFiles/'+timing_file,'r')
timing_file_content=f.read()
content_length = str(len(timing_file_content))+"\r"

message = '-----Content-Length: ' + content_length + 'filename="' +timing_file+'" Content-Type: text/plain'+'....'+timing_file_content+'-----'

response = urllib2.urlopen(controller_ip + "cmd/FILExhrBRAM", message)

