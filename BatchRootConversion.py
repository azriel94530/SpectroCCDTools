#!/usr/bin/python

###################################################################################################
# Take a path to a group of the raw FITS images from the Armin controler DAQ (the ones on which   #
# you would normally run UnshuffleFits.py).  Find the unshuffled FITS images, and then pass those #
# to Fits2Root.py for rootification and first pass analysis.                                      #
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
  print "\tUSAGE: python BatchRootConversion.py \"/path/to/the/list/of/raw/FITS/imges\""
  print "\t      (Don\'t use a \'~\' because it doesn't work with the glob package.)"
  exit()

# Pull the path to the FITS images in from the command line argument and create a list of file
# names from it.
PathToOldFitsImages = sys.argv[1]
OldFileNameList = glob.glob(PathToOldFitsImages)
print "\t...Found", len(OldFileNameList), "files."

# Now loop over all those file names and run the unshuffling program on each one.
for filename in OldFileNameList:
  UnshuffledFileName = filename.replace(".fits", "") + "/" + filename.split("/")[-1].replace(".fits", "") + "_UnShuf.fits"
  thisCommand = "python Fits2Root.py " + UnshuffledFileName
  os.system(thisCommand)

# Get the end time and report how long this calculation took
StopTime = time.time()
print "It took", StopTime - StartTime, "seconds for the batch conversion to finish."
exit()
