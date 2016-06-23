#!/bin/bash
# it expects one argument which is the directory where to run the python script
# fixed location for now
cd ~/SpectroCCD/Tools/VideoCCD

# first set the clock voltages so that all Vs and TGs are ZERO
python ccd_set_clock_voltages_before_enable.py
sleep 20

# do disable / enable
python ccd_enable_off.py
sleep 20

# enable ccd (mostly vsub) while still Vclocks are all zeros 
python ccd_enable_on.py

sleep 20
# set clocks to default
python ccd_set_clock_voltages.py

# last set the clocks and timing configuration to default values for SLOW mode
python ccd_setup_slow_mode.py
