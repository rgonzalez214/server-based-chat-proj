import socket
import time
from threading import Timer
import string
import random
import os

SERVER_IP = "127.0.0.1"
PORT = 8009
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
        return "InvalidUser"  # can still type ID is just set to invalid user


# Function to print server timeout response in case server takes too long to responnd
def timeout():
    print("Server did not respond, Timed out... Try re-logging again")


# Function to parse each message input bu the clien to do respective functions
def Parse(MESSAGE):
    match MESSAGE.lower():
        case "log on":
            print("Please wait shile we are trying to establish a connection to the chat server...")
            authorize()
        case "log off":
            print("Thank you for participating in our chat bot")
            exit(0)
    return f"{ID}{MESSAGE}"

def authorize():
    challenge_timeout = Timer(60, timeout)  # Call function timeout() in 60 seconds, 4 seconds for testing
    response_timeout = Timer(60, timeout)  # Call function timeout() in 60 seconds, 4 seconds for testing
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP Connection to the Internet
    CHALLENGE_RECEIVED = 1
    AUTH_SUCCESS = 0
    AUTH_FAIL = 1
    # Sending HELLO(Client-ID) to server
    print("Connection established! Attempting Handshake...")
    sock.sendto(bytes(f"HELLO({ID})", 'utf-8'), (SERVER_IP, PORT))

    # Waiting for CHALLENGE(rand) from server
    challenge_timeout.start()
    # INTENTIONAL FAIL
    time.sleep(5)  # For Testing : Waiting for Terrorists to win, comment-out otherwise
    if CHALLENGE_RECEIVED:
        # Bomb has been Defused
        challenge_timeout.cancel()

        # Sending RESPONSE(Client-ID, Res) to server
        print("Handshake established! Authenticating User...")
        # Insert Code Here

        # Waiting for CHALLENGE(rand) from server
        response_timeout.start()
        # INTENTIONAL FAIL
        time.sleep(5)  # For Testing : Waiting for Terrorists to win, comment-out otherwise
        if AUTH_SUCCESS:
            response_timeout.cancel()
        elif AUTH_FAIL:
            response_timeout.cancel()

def main():
    global ID
    ID = AssignID()

    # Opening a Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP Connection to the Internet

    # Parsed Input is sent as a message through the UDP Socket
    while True:
        MESSAGE = bytes(Parse(input(f"{ID} > ")), "utf-8")
        sock.sendto(MESSAGE, (SERVER_IP, PORT))
        #REPLY = sock.recvfrom(1024)
        # print("UDP target IP: %s" % SERVER_IP)
        # print("UDP target port: %s" % PORT)
        #print("%s" % str(MESSAGE, 'utf-8'))
        print("REPLY : %s\n" % str(MESSAGE, 'utf-8'))

    print("Thank you for participating in our chat bot!\n")


main()
