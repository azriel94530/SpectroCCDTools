#!/usr/bin/python

import time

from new_controller_api import *

connect_socket_to_controller()

open_controller()

controller_analog_power_on()

time.sleep(0.5)

controller_analog_power_off()

set_image_size(1440,1240)

read_register(TYPE_CCDSTATE,0)

get_image_size()

set_artificial_data(1)

close_controller()

