import socket
import struct
from new_controller_constants import *
from new_controller_messaging import mysocket


# for the messages to the controller this comes from the c struct on the server
# typedef struct {
#       int cmd;
#       int nw;
#       char strmsg[128];
#       lbnldata_t data[MAXCMDWORDS]; MAXCMDWORDS=12 (unsigned ints)
# 4-bytes per int (signed or unsigned)
#} cmdstruct_t;
 
# for the messages from the controller this comes from the c struct on the server
# typedef struct {
#        char strmsg[128];
#        lbnldata_t data[MAXRESPWORDS];
#        int status;
#} respstruct_t;
 
# message TO the controller have format:
format_ = "ii128s12i"
 
# messages FROM the controller have format:
format_from_controller_ = "128s12ii"

cmd = 0
nw = 0
string_message = ""
d00 =  0; d01 = 10; d02 =  20; d03 =  30
d04 = 40; d05 = 50; d06 =  60; d07 =  70
d08 = 80; d09 = 90; d10 = 100; d11 = 110

# maybe nice to create a class for the controller as well
sock = mysocket()

def connect_socket_to_controller():
	sock.connect('ccd-spectro.dhcp.lbl.gov', 15001)

def open_controller():
        """ Establishes a lock and a driver file descriptor, method to take ownership of controller """
        cmd = LBNL_OPEN
 
        tuple_to_send = (cmd ,nw, string_message, d00, d01, d02, d03, d04, d05, d06, d07, d08, d09, d10, d11)
        string_to_send = struct.pack(format_, *tuple_to_send)
        sock.mysend(string_to_send)
 
        # receive the reply from controller
        recv_message = sock.myreceive()
        msg_str,dr00,dr01,dr02,dr03,dr04,dr05,dr06,dr07,dr08,dr09,dr10,dr11,r_status  =  struct.unpack(format_from_controller_,recv_message)
        if (r_status != 0): print msg_str
        return r_status
 
def close_controller():
        """ Deletes lock and resets driver file descriptor, releases ownership of controller """
        cmd = LBNL_CLOSE
 
        tuple_to_send = (cmd ,nw, string_message, d00, d01, d02, d03, d04, d05, d06, d07, d08, d09, d10, d11)
        string_to_send = struct.pack(format_, *tuple_to_send)
        sock.mysend(string_to_send)
 
        # receive the reply from controller
        recv_message = sock.myreceive()
        msg_str,dr00,dr01,dr02,dr03,dr04,dr05,dr06,dr07,dr08,dr09,dr10,dr11,r_status  =  struct.unpack(format_from_controller_,recv_message)
        if (r_status != 0): print msg_str
        return r_status
 
def controller_analog_power_on():
        """ Turn ON Analog power on controller (VDD, VReset.. DC-DCs) """
 
        cmd = LBNL_POWER
        d00 = 1
        tuple_to_send = (cmd ,nw, string_message, d00, d01, d02, d03, d04, d05, d06, d07, d08, d09, d10, d11)
        string_to_send = struct.pack(format_, *tuple_to_send)
        sock.mysend(string_to_send)

 
        # receive the reply from controller
        recv_message = sock.myreceive()
        msg_str,dr00,dr01,dr02,dr03,dr04,dr05,dr06,dr07,dr08,dr09,dr10,dr11,r_status  =  struct.unpack(format_from_controller_,recv_message)
        if (r_status != 0): print msg_str
        return r_status
 
def controller_analog_power_off():
        """ Turn ON Analog power on controller (VDD, VReset.. DC-DCs) """
 
        cmd = LBNL_POWER
        d00 = 0
        tuple_to_send = (cmd ,nw, string_message, d00, d01, d02, d03, d04, d05, d06, d07, d08, d09, d10, d11)
        string_to_send = struct.pack(format_, *tuple_to_send)
        sock.mysend(string_to_send)
 
        # receive the reply from controller
        recv_message = sock.myreceive()
        msg_str,dr00,dr01,dr02,dr03,dr04,dr05,dr06,dr07,dr08,dr09,dr10,dr11,r_status  =  struct.unpack(format_from_controller_,recv_message)
        if (r_status != 0): print msg_str
        return r_status

def set_image_size(nx,ny):
        """ Set the ccd image size, with nx pixels in x and ny pixels in y """
 
        cmd = LBNL_IMSIZE
        d00 = nx
        d01 = ny
        tuple_to_send = (cmd ,nw, string_message, d00, d01, d02, d03, d04, d05, d06, d07, d08, d09, d10, d11)
        string_to_send = struct.pack(format_, *tuple_to_send)
        sock.mysend(string_to_send)
 
        # receive the reply from controller
        recv_message = sock.myreceive()
        msg_str,dr00,dr01,dr02,dr03,dr04,dr05,dr06,dr07,dr08,dr09,dr10,dr11,r_status  =  struct.unpack(format_from_controller_,recv_message)
        if (r_status != 0): print msg_str
        return r_status






