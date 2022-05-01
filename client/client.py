import socket
import threading
import time
from encodings.base64_codec import base64_encode
from threading import Timer
import logging

from cryptography.fernet import Fernet

from common import algorithms

SERVER_IP = "127.0.0.1"
PORT = 8008
hist_log = ""
temp_client = ""

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
        self.recv_buffer = ""

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


        while True:
            client_input = input(f"{self.client_id} > ")
            self.Parser(client_input)

            # Output buffered messages after receiving client input

    # Function to parse each message input by the client into protocol messages
    def Parser(self, client_input):

        if client_input == "log on":

            # Sending HELLO(Client-ID) to the server
            print("[PROTOCOL] Logging in to server... (Sending HELLO)")
            send_hello(self.sock, self.client_id)

            # Waiting for CHALLENGE(rand)
            self.sock.settimeout(10)
            data, server_address = self.sock.recvfrom(1024)

            # CHALLENGE(rand) received
            if str(data[0:9], 'utf-8') == "CHALLENGE":
                self.rand = str(data[10:-1], 'utf-8')
                self.Res = algorithms.a3(self.rand, self.secret_key)
                print(self.Res)

                # Sending RESPONSE(Client-ID, Res) to the server
                print("[PROTOCOL] CHALLENGE received! (Sending RESPONSE)")
                self.ciphering_key, size = base64_encode(bytes(algorithms.a8(self.rand, self.secret_key), 'utf-8'))
                send_response(self.sock, self.client_id, self.Res)

                # Waiting for AUTH_SUCCESS(random_cookie, TCP_Port) or AUTH FAIL
                self.sock.settimeout(10)
                data, server_address = self.sock.recvfrom(1024)

                # AUTH__ received
                if str(data[0:9], 'utf-8') == "AUTH_FAIL":
                    print("[PROTOCOL] Unable to authenticate, please try again with valid credentials!")
                else:
                    fernet = Fernet(self.ciphering_key)
                    data = fernet.decrypt(data)
                    if str(data[0:12], 'utf-8') == "AUTH_SUCCESS":
                        print("Successfully Authenticated!")
                        data = str(data, 'utf-8').split(",")
                        self.rand_cookie = data[0][13:]
                        global PORT
                        PORT = data[1][:-1]
                        self.protocol = "TCP"
        if input == "log off":
            print("Exiting Program")
            print("Thank you for participating in our chat bot!")
            exit(0)

        # if "Chat Client-ID-" in input:
        #     print(f"\nRequesting chat session with ", input[5:16])
        #     chat_request(input[5:16])

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
            print("Hello to TCP")
            data, server_address = self.sock.accept()
            process_response = threading.Thread(target=self.Processor(data))
            process_response.start()

    # Processes UDP/TCP Protocol messages
    # Changes protocol / Terminates Client
    def Processor(self, data):

        # Decrypting hashed messages
        if self.ciphering_key != None:
            fernet = Fernet(self.ciphering_key)
            data = fernet.decrypt(data)

            if str(data[0:12],'utf-8') == "AUTH_SUCCESS":
                print("Successfully Authenticated!")
                data = str(data,'utf-8').split(",")
                rand_cookie = data[1][13:]
                TCP_PORT = response[2][:-1]
                print(rand_cookie, TCP_PORT)
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
