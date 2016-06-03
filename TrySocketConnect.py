#!/usr/bin/python

import time

from new_controller_api import *

connect_socket_to_controller()

open_controller()

controller_analog_power_on()

time.sleep(2)

controller_analog_power_off()

set_image_size(1440,1240)

close_controller()

