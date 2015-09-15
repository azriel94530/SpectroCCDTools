#!/usr/bin/python

###################################################################################################
# Take a path to a group of files and run the UnshuffleFits.py script on said files with the      #
# usual number of pixel shifts.                                                                   #
###################################################################################################
# Header, import statements etc.
import time
import sys
import glob
import os

####################################
#  BEGIN MAIN BODY OF THE CODE!!!  #
####################################

# Get the start time of this calculation
StartTime = time.time()

# Check for the appropriate number of arguments, and proceed if everything looks OK.
if(len(sys.argv) != 2):
  print "\tUSAGE: python BatchUnshuffle.py \"/path/to/the/list/of/FITS/imges\""
  print "\t      (Don\'t use a \'~\' because it doesn't work with the glob package.)"
  exit()

# Pull the path to the FITS images in from the command line argument and create a list of file
# names from it.
PathToFitsImages = sys.argv[1]
print "\tReading in", PathToFitsImages
FileNameList = glob.glob(PathToFitsImages)
print "\t...Found", len(FileNameList), "files."

# Now loop over all those file names and run the unshuffling program on each one.
FinalPixelShiftNumber = 1
for filename in FileNameList:
  thisCommand = "python UnshuffleFits.py " + filename + " " + str(FinalPixelShiftNumber)
  os.system(thisCommand)

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for the batch unshuffling to finish."
exit()
