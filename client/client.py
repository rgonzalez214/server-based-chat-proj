import socket
import string
import random
import os

SERVER_IP = "127.0.0.1"
PORT = 8008


# Assigning ClientID
f1 = open("clientsIDs.txt", "r")
f2 = open("usedClientIDs.txt", "a+")
IDs = f1.readlines()
usedIDs = f2.readlines()
ID = ""

print

assigned = 0
for used in IDs:
    if used not in usedIDs:
        assigned = 1
        ID = used
        ID = ID[0:-2]
        f2.write(used)
        break
    assigned = 0
f1.close()
f2.close()

if assigned == 0:
    print("Could not assign ID, too many users! Please try again later. No free lunch in Life :)\n")

# MESSAGE = bytes(f"{ID} > ", 'UTF-8')

MESSAGE = bytes(input(f"{ID} > "), 'UTF-8')
# print("UDP target IP: %s" % SERVER_IP)
# print("UDP target port: %s" % PORT)
print("%s" % str(MESSAGE, 'utf-8'))

# sock = socket.socket(socket.AF_INET, # Internet
#                      socket.SOCK_DGRAM) # UDP
# sock.sendto(MESSAGE, (SERVER_IP, PORT))

# Generate Random Client IDs (10 character strings
# i=0
# while i < 10:
#     letters = string.ascii_lowercase
#     ID = ''.join(random.choice(letters) for i in range(10))
#     ID = ID + "\n"
#     f2 = open("server/listofsubscribers.txt", "a")
#     f1 = open("client/clientsIDs.txt", "a")
#     f1.write(ID)
#     f2.write(ID)
#     i += 1

def LogOn():
    f1 = open("clientsIDs.txt", "a+")
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
    f1 = open("clientsIDs.txt", "a+")
    ID = f1.readline()
    if not ID:
        print("No clients registered, registering client!")
        letters = string.ascii_lowercase
        ID = ''.join(random.choice(letters) for i in range(10))
        f2 = open("../server/listofsubscribers.txt", "a")
        f1.write(ID)
        f2.write(ID)
