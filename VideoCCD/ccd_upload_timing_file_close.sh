#!/bin/bash
# it expects one argument which is the directory where to run the python script
cd $1
# first set the clock voltages so that all Vs and TGs are ZERO
python ccd_upload_timing_file_close.py 

