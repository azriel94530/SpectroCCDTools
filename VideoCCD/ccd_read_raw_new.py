# python script to read an ADC image from the SpectroCCD controller (soft ARM version)
# Azriel Goldschmidt Jan-19-2016

# need still to add error handling (and remove print outputs)
# desired behaviour is passing error conditions to calling shell script

import urllib
import urllib2
import urlparse
import time
from datetime import datetime
import os
import sys


if(len(sys.argv) != 2):
  print "Usage: python Default_Directory "
  exit()
 
# 
DirectoryPath = sys.argv[1]

controller_ip = "http://192.168.1.10/"
# location of the image file to be read from the ccd/controller
output_file = DirectoryPath + "/image.fits"

# prepare the message for buffer discard and adc read operations
# here the values are hardcoded (reflecting some specific state to the checkboxes in the ADC Conversion Settings
# of the CCD timing web page (as served by the controller)
# clear/erase/epurge all checked (need to ask if these are doing anything during CCD read or buffer discard)
# idle status in idlemode (need to check if idlemode is changed when doing adc read or buffer discard)
def get_utc():
    now_utc = datetime.utcnow()
    now_utc_iso = now_utc.isoformat()
    now_utc_tosend =  now_utc_iso[0:13] + "-" + now_utc_iso[14:16] + "-" + now_utc_iso[17:19]
    return now_utc_tosend

params = "mydate="+"'"+ get_utc() +"'"+"&reply=discard&enclr=off&enera=off&enpur=off&idlestat=Idlemode%20Off"
## print "Parameters:", params

print "Discard previous image in buffer"
response = urllib2.urlopen(controller_ip + "cmd/bufdis", params)

print "ADC read"
response = urllib2.urlopen(controller_ip + "cmd/adcxhr", params)

# Get all data
html = response.read()
# print "Get all data: ", html

# Get only the length
## print "Get the length :", len(html)

# could verify here that response was OK

print "Wait for the image to read out"
not_done = True
while not_done:
    params_status = ""
    response = urllib2.urlopen(controller_ip + "cmd/adcdon", params_status)
    payload = response.read().rstrip().rstrip(",")
    payload_synt = '{' + payload + '}' 
    payload_dict = eval(payload_synt)
#    print payload_dict
#    print payload_dict['rowIndex'],payload_dict['State']

# check for timeout in the controller that would render an old stale image
# it is the bit18 thus (int(payload_dict['State'])/262144)%2

    if ( (int(payload_dict['State'])/262144)%2 == 0 and \
    not ( (int(payload_dict['State'])%16 == 12) and (payload_dict['rowIndex'] == '0'))) :
	print "There was a Timeout in the controller the image will be stale. Reduce the exposure time!"
	exit()

# wait till the least significant bits have the correct pattern

    if payload_dict['rowIndex'] == '0':
	if ( int(payload_dict['State'])%16 == 12 ) :
		not_done = False
    time.sleep(0.1)
   
print "Start download"
download_request = urllib2.urlopen(controller_ip + "image.fits")
download_response = download_request.read()

# Get the length
## print "The length of downloaded file :", len(download_response)

print "write the downloaded file to disk"

output = open(output_file,'wb')
output.write(download_response)
output.close()




