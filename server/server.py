import socket
import secrets
import threading
import logging
import chat_history

from common import algorithms

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
            print(clientID)
            break
        verified = 0
    print(clients)
    if verified == 1:
        sock.sendto(bytes(f"CHALLENGE({rand})", "utf-8"), clientAddr)
        logging.info('Sending challenge to client %s ', clientAddr)
    else:
        sock.sendto(bytes("Err:UnverifiedUser", 'utf-8'), clientAddr)
        logging.info('Client %s could not be verified', clientAddr)

def send_auth_success(rand_cookie, sock, client_address):
    sock.sendto(bytes(f"AUTH_SUCCESS({rand_cookie},{TCP_PORT})", "utf-8"), client_address)

def send_auth_fail(sock, client_address):
    sock.sendto(bytes(f"AUTH_FAIL", "utf-8"), client_address)

def send_connected():
    pass

def send_chat_started():
    pass

def send_unavailable():
    pass

def send_end_notif():
    pass

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
            process_response = threading.Thread(target=self.handle_request(data, client_address))
            process_response.start()

        except OSError as err:
            self.print(err)

    def handle_request(self, data, client_address):
        # resolve_msg = threading.Thread(target=parse(data, client_address))
        # resolve_msg.start()
        data = str(data, 'utf-8')
        if data[0:5] == "HELLO":
            rand = algorithms.rand_num()
            send_challenge(rand, client_address, data[6:-1], self.sock)
            if rand != 0:
                for id, current_client in enumerate(self.clients_list):
                    if client_address == current_client:
                        self.clients_list[id] += rand
        if data[0:8] == "RESPONSE":

            ID = data[9:19]
            Res = data[20:-1]
            rand = 0
            XRES = 0
            for id, current_client in enumerate(self.clients_list):
                if client_address == current_client:
                    rand = self.clients_list[id][3]
                else:
                    rand = 0
            if rand != 0:
                XRES = algorithms.encryptionAlgorithm(algorithms.findK(ID), rand)
            else:
                print("Error:Random number was not found!")
            # Checking to see if client was authenticated or not
            if Res == XRES:
                rand_cookie = algorithms.rand_num()
                send_auth_success(rand_cookie, client_address)
                rand_cookie()
            else:
                send_auth_fail(client_address)
        if data[0:7] == "CONNECT":
            print(data)
            send_connected()

        # S:Think if to include Client A connected messaged should be parsed through this or not
        if data[0:12] == "CHAT_REQUEST":
            # if client_available:
            #     print(MESSAGE)
            send_chat_started()
            # elif not client_available:
            #     print(MESSAGE)
            #     unavailable()

        if data[0:11] == "END_REQUEST":
            # print(MESSAGE)
            send_end_notif()

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

main()
