import socket

SERVER_IP = "127.0.0.1"
PORT = 8008
MESSAGE = b"HELLO (CLIENT-ID-A) function" # send a function as parameter not just hello? Check with TA if one message or multiple messages

print("UDP target IP: %s" % SERVER_IP)
print("UDP target port: %s" % PORT)
print("message: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (SERVER_IP, PORT))