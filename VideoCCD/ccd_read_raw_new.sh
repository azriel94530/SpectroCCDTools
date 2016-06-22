#!/bin/bash
# it expects one argument which is the directory where to run the python script
cd $1
# for now running a nominal read sequence (need to remove the discards fro it)
python ccd_read_raw_new.py $1
