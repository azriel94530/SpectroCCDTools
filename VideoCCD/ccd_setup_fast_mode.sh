#!/bin/bash
# it expects one argument which is the directory where to run the python script
# the second argument if given will be the binning (number of vertical pixels to be combined)

cd $1

binning=1

if [ "$#" -ge 2 ]; then
	binning=$2
fi

python ccd_setup_fast_mode.py $1 $binning


