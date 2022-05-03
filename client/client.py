import socket
import threading
import time
from _thread import start_new_thread

from encodings.base64_codec import base64_encode
from threading import Timer
import logging

from cryptography.fernet import Fernet

from common import algorithms

SERVER_IP = "127.0.0.1"
UDP_PORT = 8008
TCP_PORT = None

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
    sock.sendto(bytes(f"HELLO({client_id})", 'utf-8'), (SERVER_IP, UDP_PORT))


def send_response(sock, client_id, Res):
    sock.sendto(bytes(f"RESPONSE({client_id},{Res})", 'utf-8'), (SERVER_IP, UDP_PORT))


def send_connect(sock, rand_cookie, fernet):
    sock.send(fernet.encrypt(bytes(f"CONNECT({rand_cookie})", 'utf-8')))


def send_chat_request(sock, client_id, fernet):
    sock.send(fernet.encrypt(bytes(f"CHAT_REQUEST({client_id})", 'utf-8')))

def send_chat(sock, sessionID, client_input, fernet):
    sock.send(fernet.encrypt(bytes(f"CHAT({sessionID},{client_input})", 'utf-8')))

def send_end_request(sock, sessionID, fernet):
    sock.send(fernet.encrypt(bytes(f"END_REQUEST({sessionID})", 'utf-8')))

class Client:
    def __init__(self):

        self.client_id, self.secret_key = AssignIDandKey()
        self.client_connection = None
        self.rand = None
        self.rand_cookie = None
        self.Res = None
        self.ciphering_key = None
        self.sessionID = None
        self.session_client = None

        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        input_thread = threading.Thread(target=self.Sender())
        input_thread.start()


    # Function to parse each message input by the client into protocol messages
    def Sender(self):
        try:
            while True:
                time.sleep(1)
                client_input = input(f"{self.client_id} > ")
                # Authentication Phase on typing in "log on"
                if self.sessionID == None:
                    if client_input == "log on":
                        # Sending HELLO(Client-ID) to the server
                        print("[SYSTEM] Logging in to server... (Sending HELLO)")
                        send_hello(self.udp_sock, self.client_id)

                        # Waiting for CHALLENGE(rand)
                        self.udp_sock.settimeout(10)
                        data, server_address = self.udp_sock.recvfrom(1024)

                        # CHALLENGE(rand) received
                        if str(data[0:9], 'utf-8') == "CHALLENGE":
                            self.rand = str(data[10:-1], 'utf-8')
                            self.Res = algorithms.a3(self.rand, self.secret_key)

                            # Sending RESPONSE(Client-ID, Res) to the server
                            print("[SYSTEM] CHALLENGE received! (Sending RESPONSE)")
                            self.ciphering_key, size = base64_encode(
                                bytes(algorithms.a8(self.rand, self.secret_key), 'utf-8'))
                            send_response(self.udp_sock, self.client_id, self.Res)

                            # Waiting for AUTH_SUCCESS(random_cookie, TCP_Port) or AUTH FAIL
                            self.udp_sock.settimeout(10)
                            data, server_address = self.udp_sock.recvfrom(1024)

                            # AUTH__ received
                            if str(data[0:9], 'utf-8') == "AUTH_FAIL":
                                print("[SYSTEM] Unable to authenticate, please try again with valid credentials!")
                            else:
                                fernet = Fernet(self.ciphering_key)
                                data = fernet.decrypt(data)
                                if str(data[0:12], 'utf-8') == "AUTH_SUCCESS":
                                    print("[SYSTEM] Successfully Authenticated. Connecting to Chat Server...")
                                    data = str(data, 'utf-8').split(",")
                                    self.rand_cookie = data[0][13:]
                                    global TCP_PORT
                                    TCP_PORT = int(data[1][:-1])
                                    self.tcp_sock.connect((SERVER_IP, TCP_PORT))

                                    start_new_thread(self.Receiver,(self.tcp_sock,))
                                    send_connect(self.tcp_sock, self.rand_cookie, fernet)

                    elif client_input[0:4] == "chat":
                        f1 = open("clientsIDs.txt", 'r')
                        clients = f1.readlines()
                        clientID = None
                        try:
                            for client in clients:
                                if client_input[5:15] == client[0:10]:
                                    clientID = client_input[5:15]
                                    break

                            if clientID == None:
                                print("[SYSTEM] Please enter a correct 10 digit client-ID")

                            fernet = Fernet(self.ciphering_key)
                            send_chat_request(self.tcp_sock, clientID, fernet)
                        except TypeError:
                            print("[SYSTEM] Please enter a correct 10 digit client-ID")
                    elif client_input[:7] == "history":
                        try:
                            client_b = client_input[8:18].replace(" ", "")
                            if len(hist_log) > 0 and temp_client == client_b:
                                print(hist_log[-1])
                                hist_log.pop(-1)
                            #     will need to clear hist_log somewhere if new messages are saved in log
                            else:
                                # fetch history response through TCP
                                print("[PROTOCOL] Sending chat history request to server...")
                                print("prospective client_B ", client_b)
                                # send_history_request(self.sock, client_b)

                                hist_log = self.sock.recvfrom(1024)
                        except IndexError:
                            print('No history available')

                    elif client_input == "log off":
                        print("[SYSTEM] Exiting Program")
                        print("[END] Thank you for participating in our chat bot!")
                        self.tcp_sock.close()
                        exit(0)
                # While Session is engaged
                else:
                    if client_input == "End chat":
                        fernet = Fernet(self.ciphering_key)
                        send_end_request(self.tcp_sock, self.sessionID, fernet)
                        print("[SYSTEM] CHAT ENDED!")
                        self.session_client = None
                        self.sessionID = None
                    else:
                        fernet = Fernet(self.ciphering_key)
                        send_chat(self.tcp_sock, self.sessionID, client_input, fernet)
        except KeyboardInterrupt:
            pass

    # Processes UDP/TCP Protocol messages
    def Receiver(self, tcp_sock):
        try:
            while True:
                data = self.tcp_sock.recv(1024)
                # Decrypting hashed messages
                fernet = Fernet(self.ciphering_key)
                data = fernet.decrypt(data)
                # print(data)
                if str(data[0:9], 'utf-8') == "CONNECTED":
                    print(f"[SYSTEM] Connected to the chat server! Welcome, {self.client_id}.")

                elif str(data[0:12], 'utf-8') == "CHAT_STARTED":
                    self.sessionID = str(data[13:23], 'utf-8')
                    self.session_client = str(data[24:-1], 'utf-8')
                    print(f"[{self.sessionID}] CHAT STARTED with {self.session_client} (SESSION_ID: {self.sessionID})!")


                elif str(data[0:9], 'utf-8') == "END_NOTIF":
                    sessionID = str(data[10:-1], 'utf-8')
                    print(f"[{sessionID}] Chat ended by another client {self.session_client}.")
                    self.sessionID = None
                    self.session_client = None

                elif str(data[0:11], 'utf-8') == "UNREACHABLE":
                    client_id = str(data[12:-1], 'utf-8')
                    print(f"[SYSTEM] Client {client_id} is unreachable. Please try again later.")

                elif str(data[0:4], 'utf-8') == "CHAT":
                    data = str(data, 'utf-8').split(',')
                    self.sessionID = data[0][5:]
                    self.message = data[1][:-1]
                    print(f"[{self.sessionID}] {self.message}")
        except ConnectionResetError:
            print("[SYSTEM] Server closed the connection. Try restarting the program.")

        except:
            pass


def main():
    try:
        logging.getLogger().setLevel(logging.DEBUG)
        CurrentClient = threading.Thread(target=Client)
        CurrentClient.start()
    except KeyboardInterrupt:
        pass

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
