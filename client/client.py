import socket
import time
from threading import Timer
import logging

from common import algorithms

SERVER_IP = "127.0.0.1"
UDP_PORT = 8008
TCP_PORT = None
ID = ""
K = ""


# Function to assign each client an ID which is not part of usedClientIDs (currently active clients)
def AssignIDandKey():
    f1 = open("clientsIDs.txt", "r")
    f2 = open("usedClientIDs.txt", "r+")
    IDs = f1.readlines()
    usedIDs = f2.readlines()
    Assigned = False
    for newID in IDs:
        if newID not in usedIDs:
            Assigned = True
            K = newID[11:-1]
            ID = newID[0:10]
            f2.write(newID)
            return ID, K
    if not Assigned:
        print("Could not assign ID, too many active users! Please try again later. No free lunch in Life :)\n")
        return "InvalidUser", None

# Function to Authorize client on typing "log on"
def send_hello(sock):
    logging.info("Sending HELLO to server")
    sock.sendto(bytes(f"HELLO({ID})", 'utf-8'), (SERVER_IP, UDP_PORT))

def send_challenge(sock):
    # Waiting for CHALLENGE(rand) from server
    challenge, addr = sock.recvfrom(1024)
    logging.info("Received %s from server", challenge)

    # Checking for CHALLENGE success
    if str(challenge,'utf-8') != "Err:UnverifiedUser":
        print("Authenticating User...")
        challenge = str(challenge[10:-1], 'utf-8')
        sock.sendto(bytes(f"RESPONSE({ID},{algorithms.encryptionAlgorithm(K, challenge)})", 'utf-8'), (SERVER_IP, PORT))

        # Waiting for AUTHENTICATION from server
        response, addr = sock.recvfrom(1024)
        if str(response[0:12], 'utf-8') == "AUTH_SUCCESS":
            print("Successfully Authenticated!")
            response = response.split(',')
            rand_cookie = response[1][13:]
            TCP_PORT = response[2][:-1]
            print(rand_cookie, TCP_PORT)
            print("Welcome to the Chat Server.\n")
        elif str(response[0:9], 'utf-8') == "AUTH_FAIL":
            print("User could not be Authenticated... Please try again with valid credentials")
    else:
        print(f"{challenge}: Try re-logging again.")

def chat_request(Client_ID_X):
    pass

# Function to parse each message input by the client to do respective functions
def parse(input, sock):
    # Match case to non-character sensitive message
    if input == "log on":
        print("Logging in to server...")
        send_hello(sock)

        challenge, addr = sock.recvfrom(1024)
        logging.info("Received %s from server", challenge)

        # Checking for CHALLENGE success
        if str(challenge, 'utf-8') != "Err:UnverifiedUser":
            print("Authenticating User...")
            challenge = str(challenge[10:-1], 'utf-8')
            sock.sendto(bytes(f"RESPONSE({ID},{algorithms.encryptionAlgorithm(K, challenge)})", 'utf-8'),
                        (SERVER_IP, PORT))

            # Waiting for AUTHENTICATION from server
            response, addr = sock.recvfrom(1024)
            if str(response[0:12], 'utf-8') == "AUTH_SUCCESS":
                print("Successfully Authenticated!")
                response = response.split(',')
                rand_cookie = response[1][13:]
                TCP_PORT = response[2][:-1]
                print(rand_cookie, TCP_PORT)
                print("Welcome to the Chat Server.\n")
            elif str(response[0:9], 'utf-8') == "AUTH_FAIL":
                print("User could not be Authenticated... Please try again with valid credentials")
        else:
            print(f"{challenge}: Try re-logging again.")

    if input == "log off":
            print("Thank you for participating in our chat bot!")
            exit(0)

    if "Chat Client-ID-" in input:
        print(f"\nRequesting chat session with ", input[5:16])
        chat_request(input[5:16])
    return input


def main():
    logging.getLogger().setLevel(logging.DEBUG)

    # Assigning Client ID and Key
    global ID
    global K
    ID, K = AssignIDandKey()

    # Opening a Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP Connection to the Internet

    # Loop to parse through each message from the client
    while True:
        parse(input(f"{ID} > ").lower(), sock)

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
