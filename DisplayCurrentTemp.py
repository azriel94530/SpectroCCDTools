#! /home/user/anaconda/bin/python
# Just dump the current temperature to the terminal screen.
import LakeShoreTools
import socket
LS325_IP   = "192.168.1.46"
LS325_PORT = 9001
LS325Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
LS325Socket.settimeout(3)
LS325Socket.connect((LS325_IP,LS325_PORT))
print "Current Temperature:", LakeShoreTools.ReadCurrentTemp(LS325Socket), "C."

