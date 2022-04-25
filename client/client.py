import socket
import time
from threading import Timer
import string
import random
import os
import hashlib

SERVER_IP = "127.0.0.1"
PORT = 8008
ID = ""
K = ""

def encryptionAlgorithm(key, rand):
    k = int(key,16)
    m = int(rand,16)
    kb = bin(k)[6:]
    mb = bin(m)[4:]
    kbl = kb[0:64]
    kbr = kb[64:]
    mbl = mb[0:64]
    mbr = mb[64:]
    a1 = int(kbl, 2)^int(mbr, 2)
    a2 = int(kbr, 2)^int(mbl, 2)
    a3 = a1^a2
    a4 = bin(a3)[2:].zfill(64)
    a5 = a4[0:32]
    a6 = a4[32:]
    a7 = int(a5, 2)
    int(a6, 2)
    return bin(a7)[2:].zfill(len(a5))

# Function to assign each client an ID which is not part of usedClientIDs (currently active clients)
def AssignIDandKey():
    # Each client is assigned a pre-selected unique 10-character string as an ID
    # While a client is "active" (has not logged-off), their IDs are
    # stored in client/usedClientIDs.txt for unique assignment of IDs
    f1 = open("clientsIDs.txt", "r")
    f2 = open("usedClientIDs.txt", "r+")
    IDs = f1.readlines()
    usedIDs = f2.readlines()
    assigned = 0
    for newID in IDs:
        if newID not in usedIDs:
            assigned = 1
            ID = newID
            K = ID[11:-1]
            ID = ID[0:10]
            f2.write(newID)
            return ID, K
        assigned = 0
    f1.close()
    f2.close()

    if assigned == 0:
        print("Could not assign ID, too many users! Please try again later. No free lunch in Life :)\n")
        return "InvalidUser"  # can still type ID is just set to invalid user

# Function to print server timeout response in case server takes too long to responnd
def timeout():
    print("Server did not respond, timed out... Try re-logging again.")

# Function to Authorize client on typing "log on"
def authorize():
    challenge_timeout = Timer(4, timeout)  # Call function timeout() in 60 seconds, 4 seconds for testing
    response_timeout = Timer(4, timeout)  # Call function timeout() in 60 seconds, 4 seconds for testing
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP Connection to the Internet
    AUTH_SUCCESS = 1
    AUTH_FAIL = 0
    # Sending HELLO(Client-ID) to server
    print("Connection established! Attempting Handshake...")
    sock.sendto(bytes(f"HELLO({ID})", 'utf-8'), (SERVER_IP, PORT))

    # Waiting for CHALLENGE(rand) from server
    challenge_timeout.start()
    challenge, addr = sock.recvfrom(1024)
    challenge_timeout.cancel()

    # Checking for CHALLENGE success
    if str(challenge,'utf-8') != "Err:UnverifiedUser":
        print("Authenticating User...")
        challenge = str(challenge[10:-1], 'utf-8')
        sock.sendto(bytes(f"RESPONSE({ID},{encryptionAlgorithm(K, challenge)})", 'utf-8'), (SERVER_IP, PORT))

        # Waiting for AUTHENTICATION from server
        response_timeout.start()
        response, addr = sock.recvfrom(1024)
        response_timeout.cancel()
        if str(response[0:12], 'utf-8') == "AUTH_SUCCESS":
            print("Successfully Authenticated!")
            print("Welcome to the Chat Server.\n")
        elif str(response[0:9], 'utf-8') == "AUTH_FAIL":
            print("User could not be Authenticated... Please try again with valid credentials")
    else:
        print(f"{challenge}: Try re-logging again.")



# Function to parse each message input by the client to do respective functions
def parse(input):
    # Match case to non-character sensitive message
    if input == "log on":
            print("\nPlease wait while we are trying to establish a connection to the chat server...")
            authorize()

    if input == "log off":
            print("Thank you for participating in our chat bot!")
            exit(0)
    return input


def main():
    global ID
    global K
    ID, K = AssignIDandKey()

    # Opening a Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP Connection to the Internet

    # Loop to parse through each message from the client
    while True:
        parse(input(f"{ID} > ").lower())
        # sock.sendto(MESSAGE, (SERVER_IP, PORT))
        # REPLY = sock.recvfrom(1024)
        # print("MESSAGE : %s\n" % str(MESSAGE, 'utf-8'))
        # print("REPLY : %s\n" % str(REPLY, 'utf-8'))


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
