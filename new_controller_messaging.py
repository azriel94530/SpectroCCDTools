import socket

MSGLEN_TO_CONTROLLER = 184
MSGLEN_FROM_CONTROLLER = 180

class mysocket:
    '''demonstration class only
      - coded for clarity, not efficiency
    '''
 
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
 
    def connect(self, host, port):
        self.sock.connect((host, port))
 
    def mysend(self, msg):
        totalsent = 0
        while totalsent < MSGLEN_TO_CONTROLLER:
            sent = self.sock.send(msg[totalsent: MSGLEN_TO_CONTROLLER])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
 
    def myreceive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN_FROM_CONTROLLER:
            chunk = self.sock.recv(min(MSGLEN_FROM_CONTROLLER - bytes_recd, 2048))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return ''.join(chunks)

