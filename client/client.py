import socket
import string
import random
import os

SERVER_IP = "127.0.0.1"
PORT = 8008

# Assigning ClientID
f1 = open("clientIDs.txt", "r")
f2 = open("usedClientIDs.txt", "a+")
ID = ""
if os.path.getsize("usedClientIDs.txt") == 0:
    ID = f1.readline()
    ID = ID[0:-2]
    f2.write(ID)
    f2.write("\n")
else:
    SN = 0
    while SN<0:
        print(f2.readline())
        SN = SN + 1
    print(SN)
    while SN > 0:
        f1.readline()
        SN = SN - 1
    ID = f1.readline()
    ID = ID[0:-2]
    f2.write(ID)
    f2.write("\n")

MESSAGE = bytes(input(f"{ID} > "), 'UTF-8')
# print("UDP target IP: %s" % SERVER_IP)
# print("UDP target port: %s" % PORT)
print(ID, "message: %s" % str(MESSAGE, 'utf-8'))

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (SERVER_IP, PORT))

# Generate Random Client IDs (10 character strings
# i=0
# while i < 10:
#     letters = string.ascii_lowercase
#     ID = ''.join(random.choice(letters) for i in range(10))
#     ID = ID + "\n"
#     f2 = open("server/listofsubscribers.txt", "a")
#     f1 = open("client/clientIDs.txt", "a")
#     f1.write(ID)
#     f2.write(ID)
#     i += 1

def LogOn():
    f1 = open("clientIDs.txt", "a+")
    ID = f1.readline()
    if not ID:
        print("No clients registered, registering client!")
        letters = string.ascii_lowercase
        ID = ''.join(random.choice(letters) for i in range(10))
        f2 = open("../server/listofsubscribers.txt", "a")
        f1.write(ID)
        f2.write(ID)
        HELLO(ID)
    else:
        HELLO(ID)

def HELLO(ClientID):
    f1 = open("clientIDs.txt", "a+")
    ID = f1.readline()
    if not ID:
        print("No clients registered, registering client!")
        letters = string.ascii_lowercase
        ID = ''.join(random.choice(letters) for i in range(10))
        f2 = open("../server/listofsubscribers.txt", "a")
        f1.write(ID)
        f2.write(ID)
