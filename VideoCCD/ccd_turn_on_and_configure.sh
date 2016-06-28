#!/bin/bash
# it expects one argument which is the directory where to run the python script
# the second argument if given will be the binning (number of vertical pixels to be combined)

directory="/home/user/SpectroCCD/Tools/VideoCCD/"

if [ "$#" -ge 1 ]; then
	directory=$1
fi

cd $directory

binning=1

if [ "$#" -ge 2 ]; then
	binning=$2
fi

python ccd_turn_on_and_configure.py $1 $binning

echo "Done"

sleep 2

