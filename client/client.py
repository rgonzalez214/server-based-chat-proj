import socket
import signal
import string
import random
import os

SERVER_IP = "127.0.0.1"
PORT = 8008
ID = ""

# Assigning ClientID
def AssignID():
    f1 = open("clientsIDs.txt", "r")
    f2 = open("usedClientIDs.txt", "r+")
    IDs = f1.readlines()
    usedIDs = f2.readlines()
    assigned = 0
    for used in IDs:
        if used not in usedIDs:
            assigned = 1
            ID = used
            ID = ID[0:-2]
            f2.write(used)
            return ID
        assigned = 0
    f1.close()
    f2.close()

    if assigned == 0:
        print("Could not assign ID, too many users! Please try again later. No free lunch in Life :)\n")
        return "InvalidUser"

def Parse(MESSAGE):
    match MESSAGE.lower():
        case "log on":
            Authorize()
        case "log off":
            print("Thank you for participating in our chat bot!\n")
            exit(0)

    if MESSAGE.lower() == "log on":
        Authorize()
    if MESSAGE.lower() == "log off":
        return f"InsertFunctionHere({ID})\n"


def Authorize():
    #Send Hello
    #Challenge Wait
    #Send Response
    #Auth Wait
    return 0



# Generate Random Client IDs (10 character strings)
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

def main():
    global ID
    ID = AssignID()

    # Opening a Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Connection to the Internet

    # Parsed Input is sent as a message through the UDP Socket
    flag = 1
    while True:

        MESSAGE = bytes(Parse(input(f"{ID} > ")), "utf-8")
        sock.sendto(MESSAGE, (SERVER_IP, PORT))
        REPLY = sock.recvfrom(1024)
        # print("UDP target IP: %s" % SERVER_IP)
        # print("UDP target port: %s" % PORT)
        print("MESSAGE : %s\n" % str(MESSAGE, 'utf-8'))
        print("REPLY : %s\n" % str(REPLY, 'utf-8'))

    print("Thank you for participating in our chat bot!\n")

main()