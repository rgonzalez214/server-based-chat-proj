import socket
import secrets
import threading
import logging
import chat_history

HOST_IP = "127.0.0.1"
UDP_PORT = 8008
TCP_PORT = 4761

def send_challenge(rand, clientAddr, clientID, sock):

    # Verify on listofsubs
    f1 = open("listofsubscribers.txt", "r")
    clients = f1.readlines()
    verified = 0
    for client in clients:
        if clientID == client[0:10]:
            verified = 1
            break
        verified = 0

    if verified == 1:
        sock.sendto(bytes(f"CHALLENGE({rand})", "utf-8"), clientAddr)
        logging.info('Sending challenge to client %s ', clientAddr)
    else:
        sock.sendto(bytes("Err:UnverifiedUser", 'utf-8'), clientAddr)
        logging.info('Client %s could not be verified', clientAddr)

def auth_success(rand_cookie, sock, client_address):
    sock.sendto(bytes(f"AUTH_SUCCESS({rand_cookie},{TCP_PORT})", "utf-8"), client_address)

def auth_fail(sock, client_address):
    sock.sendto(bytes(f"AUTH_FAIL", "utf-8"), client_address)

def connected():
    pass

def chat_started():
    pass

def unavailable():
    pass

def end_notif():
    pass

# Function to parse client messages based on message sent by a certain client.
# def parse(MESSAGE, clientAddr, client_available=True):

class UDPServer:
    def __init__(self):
        logging.info("Initializing UDP Broker")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Welcoming socket for UDP
        self.sock.bind((HOST_IP, UDP_PORT))
        self.clients_list = []
        # self.clients_info = []

        while True:
            self.wait_for_client()

    # Wait for a new client to connect
    def wait_for_client(self):
        try:
            # Receive data from client
            data, client_address = self.sock.recvfrom(1024)
            logging.info('Received data from client %s: %s', client_address, data)

            # Add client to list of clients
            if client_address not in self.clients_list:
                self.clients_list.append(client_address)
            print(self.clients_list)


            # Handle client request
            self.handle_request(self.sock, data, client_address)

        except OSError as err:
            self.print(err)

    def handle_request(self, sock, data, client_address):
        # resolve_msg = threading.Thread(target=parse(data, client_address))
        # resolve_msg.start()
        if data[0:5] == "HELLO":
            rand = common.algorithms.rand_num()
            send_challenge(rand, client_address, data[6:-1])
            if rand != 0:
                for current_client in self.clients_list:
                    if client_address == current_client:
                        self.clients_list[current_client] += rand
        if data[0:8] == "RESPONSE":
            ID = str(data[9:19], 'utf-8')
            Res = str(data[20:-1], 'utf-8')
            rand = 0
            XRES = 0
            for current_client in self.clients_list:
                if client_address == current_client:
                    rand = self.clients_list[current_client][3]
                else:
                    rand = 0
            if rand != 0:
                XRES = encryptionAlgorithm(findK(ID), rand)
            else:
                print("Error:Random number was not found!")
            # Checking to see if client was authenticated or not
            if Res == XRES:
                rand_cookie = rand_num()
                auth_success(rand_cookie, client_address)
                rand_cookie()
            else:
                auth_fail(client_address)
        if data[0:7] == "CONNECT":
            print(data)
            connected()

        # S:Think if to include Client A connected messaged should be parsed through this or not
        if data[0:12] == "CHAT_REQUEST":
            # if client_available:
            #     print(MESSAGE)
            chat_started()
            # elif not client_available:
            #     print(MESSAGE)
            #     unavailable()

        if data[0:11] == "END_REQUEST":
            # print(MESSAGE)
            end_notif()

        if data[0:4] == "CHAT":
            # print(MESSAGE)
            print("chat_history.write_log()")

        if data[0:11] == "HISTORY_REQ":
            # print(MESSAGE)
            chat_history.read_log("abcd", "efgh")

class TCPServer:
    def __init__(self):
        logging.info("Initializing TCP Broker")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Welcoming socket for UDP
        self.sock.bind((HOST_IP, TCP_PORT))
        self.clients_list = []

        while True:
            self.wait_for_client()

    # Wait for a new client to connect
    def wait_for_client(self):
        try:
            # Receive data from client
            data, client_address = self.sock.recvfrom(1024)
            logging.info('Received data from client %s: %s', client_address, data)

            # Add client to list of clients
            if client_address not in self.clients_list:
                self.clients_list.append(client_address)
            logging.info(self.clients_list)

            # Handle client request
            process_response = threading.Thread(target=parse(data, client_address))
            process_response.start()

        except OSError as err:
            self.printwt(err)


def main():

    logging.getLogger().setLevel(logging.DEBUG)
    UDPHandler = threading.Thread(target=UDPServer)
    TCPHandler = threading.Thread(target=TCPServer)

    UDPHandler.start()
    TCPHandler.start()

    # global UDPsocket
    # print("[STARTING] server is starting...")
    # UDPsocket.bind((HOST_IP, UDP_PORT)) # UDP socket bound
    # print(f"[STARTING] server is running on {HOST_IP}:{UDP_PORT}")
    #
    # while True:
    #     message, addr = UDPsocket.recvfrom(1024) # buffer size is 1024 bytes
    #     print("SERVER-received message: %s" % message)
    #     parse(str(message, 'utf-8'), addr)

        # # update client_B_ID--------------------------------
        # client_B_ID = 'client789'
        # print("client-A-ID is: ", client_A_ID)
        # print("client-B-ID is: ", client_B_ID)
        #
        # #  sliced message to separate payload
        # payload = str(data[9:], 'utf-8')
        # print("payload is: ", payload)
        # if payload[:7].lower().strip() == 'history':
        #     print(payload[7:].lower().strip())
        #     chat_history.read_log(client_A_ID, payload[7:].lower().strip())
        #
        # #  sliced message to separate payload
        # if payload[:6].lower() == 'log on':
        #     print("initiate log on")
        #     connect("CONNECTED")
        # clients= [client_A_ID, client_B_ID]
        # #res = chat_started(clients, payload)
        # #print(res)

main()

# 1. Check if client is on list of subscribers
# 2. Retrieve the client’s secret key and send a CHALLENGE (rand) message to the client, using UDP
# 3. Wait for RESPONSE from client.
# 4.1 If authentication is not successful, the server sends an AUTH_FAIL message to the client.
# 4.2 Else generate an encryption key CK-A, then sends an AUTH_SUCCESS(rand_cookie, port_number) message to the client. The message is encrypted by CK-A.
# From this point on, all data exchanged between client A and the server is encrypted using CK-A.
# 5. Wait for TCP connection request from client.
# From this point on, until the TCP connection is closed, all data (signaling messages and chat) is exchanged over the TCP connection.
# 6. The server sends CONNECTED to the client. The client is connected.
# 7. If client types “Log off” or when the activity timer expires, the TCP connection is closed.

# Client A Initiates Chat Session to B
# This scenario will go through the following steps.
# Client A must have already gone through the connection phase and be connected to the server.
#     End user types “Chat Client-ID-B” (client A sends a CHAT_REQUEST (Client-ID-B)).
#         - If the server determines client-B is connected and not already engaged in another chat session
#             1. The server sends CHAT_STARTED(session-ID, Client-ID-B) to client A
#             2. The server sends CHAT_STARTED(session-ID, Client-ID-A) to client B
#             3. Client A and Client B are now engaged in a chat session and can send chat messages with each other, through the server.
#             4. The clients display “Chat started” to the end user at A and B.
#         - If client B is not available, the server sends UNREACHABLE (Client-ID-B) to client A.
#
# Client A or B chooses to end chat session.
#     End user types “End Chat”, (Client sends END_REQUEST (session-ID) to the server).
#         1. The server sends an END_NOTIF(session-ID) to the other client.
#         2. The Clients display “Chat ended” to their respective end users.
