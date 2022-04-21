import socket
import time
from threading import Timer
import string
import random
import os

SERVER_IP = "127.0.0.1"
PORT = 8008
ID = ""

# Function to assign each client an ID which is not part of usedClientIDs (currently active clients)
def AssignID():
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
            ID = ID[0:-2]
            f2.write(newID)
            return ID
        assigned = 0
    f1.close()
    f2.close()

    if assigned == 0:
        print("Could not assign ID, too many users! Please try again later. No free lunch in Life :)")
        return "InvalidUser"

# Function to print server timeout response incase server takes too long to respond
def timeout():
    print("Server did not respond, timed out... Try re-logging again.")

# Function to parse each message input by the client to do respective functions
def parse(MESSAGE):
    # Match case to non-character sensitive message
    match MESSAGE.lower():
        case "log on":
            print("Please wait while we are trying to establish a connection to the chat server...")
            authorize()
        case "log off":
            print("Thank you for participating in our chat bot!")
            exit(0)
    return f"{MESSAGE}"

# Function to Authorize client on typing "log on"
def authorize():
    challenge_timeout = Timer(4, timeout)  # Call function timeout() in 60 seconds, 4 seconds for testing
    response_timeout = Timer(4, timeout)  # Call function timeout() in 60 seconds, 4 seconds for testing
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
    time.sleep(5)                       # For Testing : Waiting for Terrorists to win, comment-out otherwise
    if CHALLENGE_RECEIVED and challenge_timeout.is_alive():
        # Bomb has been Defused
        challenge_timeout.cancel()

        # Sending RESPONSE(Client-ID, Res) to server
        print("Handshake established! Authenticating User...")

        # Insert Code Here

        # Waiting for CHALLENGE(rand) from server
        response_timeout.start()
        # INTENTIONAL FAIL
        time.sleep(5)  # For Testing : Waiting for Terrorists to win, comment-out otherwise
        if AUTH_SUCCESS and response_timeout.is_alive():
            response_timeout.cancel()
        elif AUTH_FAIL and response_timeout.is_alive():
            response_timeout.cancel()

    # Do nothing so input goes back to main for client to re-try login

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

# Main Function to drive the program
def main():
    # Assigning unique ID to client
    global ID
    ID = AssignID()

    # Opening a Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Connection to the Internet

    # Loop to parse through each message from the client
    while True:
        MESSAGE = bytes(parse(input(f"{ID} > ")), 'utf-8')
        sock.sendto(MESSAGE, (SERVER_IP, PORT))
        REPLY = sock.recvfrom(1024)
        # print("MESSAGE : %s\n" % str(MESSAGE, 'utf-8'))
        print("REPLY : %s\n" % str(REPLY, 'utf-8'))


main()