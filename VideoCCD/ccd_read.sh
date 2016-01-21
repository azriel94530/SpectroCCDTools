#!/bin/bash
# it expects one argument which is the directory where to run the python script
cd $1
python ccd_read.py $1
