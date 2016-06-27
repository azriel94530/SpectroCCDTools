#!/bin/bash
# it expects one argument which is the directory where to run the python script
# fixed location for now
cd ~/SpectroCCD/Tools/VideoCCD

# first set the clock voltages so that all Vs and TGs are ZERO
echo "Setting clock voltage values to prepare for reset"
python ccd_set_clock_voltages_before_enable.py
sleep 20

# do disable / enable
echo "Disabling CCD"
python ccd_enable_off.py
sleep 20

# enable ccd (mostly vsub) while still Vclocks are all zeros 
echo "Enabling CCD"
python ccd_enable_on.py

sleep 20
# set clocks to default
echo "Set clock voltages to nominal"
python ccd_set_clock_voltages.py

# last set the clocks and timing configuration to default values for SLOW mode
echo "Set up for slow mode acquisitions"
python ccd_setup_slow_mode.py

echo "Done"

sleep 2

