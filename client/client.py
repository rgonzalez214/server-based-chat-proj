import socket
import threading
import time
from threading import Timer
import logging

from cryptography.fernet import Fernet

from common import algorithms

SERVER_IP = "127.0.0.1"
PORT = 8008

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
def send_hello(sock, client_id):
    logging.info("Sending HELLO to server")
    sock.sendto(bytes(f"HELLO({client_id})", 'utf-8'), (SERVER_IP, PORT))

def send_response(sock, client_id, Res):
    sock.sendto(bytes(f"RESPONSE({client_id},{Res})", 'utf-8'), (SERVER_IP, PORT))

def chat_request(Client_ID_X):
    pass


class Client:
    def __init__(self):
        self.client_id, self.secret_key = AssignIDandKey()
        self.rand = None
        self.rand_cookie = None
        self.Res = None
        self.ciphering_key = None
        self.protocol = "UDP"
        self.sock =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_buffer = ""

        # Start actively listening for messages
        constantly_receive_messages = threading.Thread(target=self.Receiver())
        constantly_receive_messages.start()

        while True:
            client_input = input(f"{ID} > ")
            process_input = threading.Thread(target=self.Parser(client_input))
            process_input.start()
            # Output buffered messages after receiving client input

    # Function to parse each message input by the client into protocol messages
    def Parser(self, client_input):
        if client_input == "log on":
            # Sending HELLO(Client-ID) to the server
            print("Logging in to server...")
            send_hello(self.sock)

        if input == "log off":
            print("Exiting Program")
            print("Thank you for participating in our chat bot!")
            exit(0)

        if "Chat Client-ID-" in input:
            print(f"\nRequesting chat session with ", input[5:16])
            chat_request(input[5:16])

    # Driver function for receiving UDP/TCP Protocol messages
    def Receiver(self):
        while self.protocol == "UDP":
            data, server_address = self.sock.recvfrom(1024)
            process_response = threading.Thread(target=self.Processor(data))
            process_response.start()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((SERVER_IP, PORT))
        self.sock.listen()
        while True:
            data, server_address = self.sock.accept()
            process_response = threading.Thread(target=self.Processor(data))
            process_response.start()

    # Processes UDP/TCP Protocol messages
    # Changes protocol / Terminates Client
    def Processor(self, data):

        # CHALLENGE(rand) received
        if str(data[0:9],'utf-8') == "CHALLENGE":
            self.rand = str(data[10:-1],'utf-8')
            # Fix Response processing by the server
            self.Res = algorithms.a3(self.rand, self.secret_key)
            send_response(self.sock, self.client_id, self.Res)
            self.ciphering_key = algorithms.a8(self.rand, self.secret_key)

        # AUTH_FAIL received
        elif str(data[0:9],'utf-8') == "AUTH_FAIL":
            print("User could not be Authenticated... Please try again with valid credentials")

        # Decrypting hashed messages
        elif self.ciphering_key != None:
            fernet = Fernet(self.ciphering_key)
            data = fernet.decrypt(data)

            if str(data[0:12],'utf-8') == "AUTH_SUCCESS":
                print("Successfully Authenticated!")
                data = str(data,'utf-8').split(",")
                print(data)
                # rand_cookie = data[1][13:]
                # TCP_PORT = response[2][:-1]
                # print(rand_cookie, TCP_PORT)
            print("Welcome to the Chat Server.\n")

        # Garbage Output by server
        else:
            print("Server sent garbage: %s", str(data,'utf-8'))

def main():

    logging.getLogger().setLevel(logging.DEBUG)
    CurrentClient = threading.Thread(target=Client)
    CurrentClient.start()

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
