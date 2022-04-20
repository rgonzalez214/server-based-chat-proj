import socket
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

    if MESSAGE.lower() == f"{ID}log on":
        return f"HELLO({ID})\n"                                   # ASK THE TA!!!
    if MESSAGE.lower() == f"{ID}log off":
        return f"InsertFunctionHere({ID})\n"                                   # ASK THE TA!!!
    else:
        return f"{ID}{MESSAGE}"


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

def HELLO(ClientID):
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

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
        # print("UDP target IP: %s" % SERVER_IP)
        # print("UDP target port: %s" % PORT)
        # print("%s" % str(MESSAGE, 'utf-8'))

    print("Thank you for participating in our chat bot!\n")

main()


"""
--Client A Initiates Chat Session to B--
Client A must have already gone through the connection phase and be connected to the server.
    - End user types “Chat Client-ID-B” (client A sends a CHAT_REQUEST (Client-ID-B)).
        1. The server sends CHAT_STARTED(session-ID, Client-ID-B) to client A
        2. The server sends CHAT_STARTED(session-ID, Client-ID-A) to client B
        3. Client A and Client B are now engaged in a chat session and can send chat messages with each other, through the server. 
        4. The clients display “Chat started” to the end user at A and B. 
       
--Client A or B Terminates Chat Session---
    - End user types “End Chat”, (Client sends END_REQUEST (session-ID) to the server). 
        1. The server sends an END_NOTIF(session-ID) to the other client. 
        2. The Clients display “Chat ended” to their respective end users.

"""