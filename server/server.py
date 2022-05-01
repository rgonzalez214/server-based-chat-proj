import socket
import secrets
import threading
import logging
from encodings.base64_codec import base64_encode

import chat_history

from cryptography.fernet import Fernet
from common import algorithms

HOST_IP = "127.0.0.1"
UDP_PORT = 8008
TCP_PORT = 4761

def send_challenge(sock, currentClient, rand):
    logging.info('Sending CHALLENGE to client %s ', currentClient.client_address)
    sock.sendto(bytes(f"CHALLENGE({rand})", "utf-8"), currentClient.client_address)

def send_auth_success(sock, currentClient, fernet):
    logging.info('Sending AUTH_SUCCESS to client %s ', currentClient.client_address)
    sock.sendto(fernet.encrypt(bytes(f"AUTH_SUCCESS({currentClient.rand},{TCP_PORT})", "utf-8")), currentClient.client_address)

def send_auth_fail(sock, currentClient):
    logging.info('Sending AUTH_FAIL to client %s ', currentClient.client_address)
    sock.sendto(bytes(f"AUTH_FAIL", "utf-8"), currentClient.client_address)

def send_connected(sock, currentClient):
    logging.info('Sending CONNECTED to client %s ', currentClient.client_address)
    sock.sendto(bytes("CONNECTED TO SERVER", "utf-8"))

def send_chat_started():
    pass

def send_unavailable():
    pass

def send_end_notif():
    pass

class Client:
    def __init__(self, client_address):
        self.client_address = client_address
        self.client_id = None
        self.secret_key = None
        self.ciphering_key = None
        self.rand = None
        self.XRES = None
        self.session_ID = None

    def set_client_id(self, clientID):
        self.client_id = clientID

class UDPServer:
    def __init__(self):
        logging.info("Initializing UDP Broker")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Welcoming socket for UDP
        self.sock.bind((HOST_IP, UDP_PORT))
        self.clients_list = []

        while True:
            self.wait_for_client()

    def returnClient(self, client_address):
        client_address

    # Wait for a new client to connect
    def wait_for_client(self):
        try:
            # Receive data from client
            data, client_address = self.sock.recvfrom(1024)
            newClient = Client(client_address)
            logging.info('Received data from client %s: %s', newClient.client_address, data)

            # Add client to list of clients
            if self.clients_list == []:
                self.clients_list.append(newClient)
                logging.info("New Client Connection Registered")
            else:
                # Checking to see if the client exists on the current list of clients or not
                client_exists = False
                for i, each_client in enumerate(self.clients_list):
                    if newClient.client_address == each_client.client_address:
                        newClient = self.clients_list[i]
                        client_exists = True
                        break

                if not client_exists:
                    self.clients_list.append(newClient)
                    logging.info("New Client Connection Registered")

            process_response = threading.Thread(target=self.handle_client(data, newClient))
            process_response.start()
        except OSError:
            print("OSError in UDP Server")

    def handle_client(self, data, current_client):
        data = str(data, 'utf-8')
        # HELLO(Client-ID) Received
        if data[0:5] == "HELLO":
            current_client.client_id = data[6:-1]
            # Verify if the client is on the list of Subscribers
            if algorithms.verify(current_client.client_id):
                # Find Client Secret Key
                current_client.secret_key = algorithms.findSecretKey(current_client.client_id)
                if current_client.secret_key == -1:
                    logging.info(f"{current_client.client_id}: Could not find client Secret Key!")
                else:
                    # Client verified and secret key obtained
                    # Generate a random number, generate XRES and send client the CHALLENGE
                    current_client.rand = algorithms.rand_num()
                    current_client.XRES = algorithms.a3(current_client.rand, current_client.secret_key)
                    send_challenge(self.sock, current_client, current_client.rand)
            else:
                logging.info(f"{current_client.client_id}: Could not verify client!")

        # RESPONSE(Res) received
        if data[0:8] == "RESPONSE":
            data = data.split(",")
            if current_client.client_id != data[0][9:] or current_client.XRES != data[1][:-1]:
                send_auth_fail(self.sock, current_client)
            else:
                current_client.ciphering_key, size = base64_encode(bytes(algorithms.a8(current_client.rand, current_client.secret_key), 'utf-8'))
                fernet = Fernet(current_client.ciphering_key)
                send_auth_success(self.sock, current_client, fernet)

        self.updateClient(current_client)

    def updateClient(self, newClient):
        for i, currentClient in enumerate(self.clients_list):
            if currentClient.client_address == newClient.client_address:
                self.clients_list[i] = newClient
                break


class TCPServer:
    def __init__(self):
        logging.info("Initializing TCP Broker")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Welcoming socket for TCP
        self.sock.bind((HOST_IP, TCP_PORT))
        self.sock.listen()
        self.clients_list = []

        while True:
            data, client_address = self.sock.accept()
            process_response = threading.Thread(target=self.handle_client(data, client_address))
            process_response.start()

    def handle_client(self, data, client_address):
        if data[0:7] == "CONNECT":
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


def main():

    logging.getLogger().setLevel(logging.DEBUG)
    UDPHandler = threading.Thread(target=UDPServer)
    TCPHandler = threading.Thread(target=TCPServer)

    UDPHandler.start()
    TCPHandler.start()

main()
