import socket
import threading
import logging
import time
from _thread import start_new_thread

from cryptography.fernet import Fernet
from encodings.base64_codec import base64_encode

from common import algorithms
import chat_history


HOST_IP = "127.0.0.1"
UDP_PORT = 8008
TCP_PORT = 4761

def send_challenge(sock, currentClient, rand):
    sock.sendto(bytes(f"CHALLENGE({rand})", "utf-8"), currentClient.client_address)

def send_auth_success(sock, currentClient, fernet):
    sock.sendto(fernet.encrypt(bytes(f"AUTH_SUCCESS({currentClient.rand},{TCP_PORT})", "utf-8")), currentClient.client_address)

def send_auth_fail(sock, currentClient):
    logging.info('Sending AUTH_FAIL to client %s ', currentClient.client_address)
    sock.sendto(bytes(f"AUTH_FAIL", "utf-8"), currentClient.client_address)

def send_connected(currentClient, fernet):
    currentClient.client_connection.send(fernet.encrypt(bytes("CONNECTED", "utf-8")))

def send_chat_started(sessionID, currentClient, requestedClient):
    fernet = Fernet(currentClient.ciphering_key)
    currentClient.client_connection.send(fernet.encrypt(bytes(f"CHAT_STARTED({sessionID},{requestedClient.client_id})", "utf-8")))

def send_unreachable(currentClient, client_id):
    fernet = Fernet(currentClient.ciphering_key)
    currentClient.client_connection.send(fernet.encrypt(bytes(f"UNREACHABLE({client_id})", "utf-8")))

def send_endnotif(requestedClient):
    fernet = Fernet(requestedClient.ciphering_key)
    requestedClient.client_connection.send(fernet.encrypt(bytes(f"END_NOTIF({requestedClient.sessionID})", "utf-8")))

def send_chat(currentClient, requestedClient, message):
    fernet = Fernet(requestedClient.ciphering_key)
    requestedClient.client_connection.send(fernet.encrypt(bytes(f"CHAT({currentClient.sessionID},{message})", "utf-8")))

def send_history_resp(currentClient, requestedClient, message):
    pass

transitioning_client = None

class Client:
    def __init__(self, client_address):
        self.sock = None
        self.client_address = client_address
        self.client_connection = None
        self.authenticated = False
        self.client_id = None
        self.secret_key = None
        self.ciphering_key = None
        self.rand = None
        self.XRES = None
        self.sessionID = None

class UDPServer:
    def __init__(self):
        logging.info("Initializing UDP Broker")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Welcoming socket for UDP
        self.sock.bind((HOST_IP, UDP_PORT))
        self.clients_list = []
        while True:
            self.wait_for_client()

    # Wait for a new client to connect
    def wait_for_client(self):
        try:
            # Receive data from client
            data, client_address = self.sock.recvfrom(1024)
            newClient = Client(client_address)
            logging.info(f"[UDP] {str(data, 'utf-8')}")
            # Add client to list of clients
            if self.clients_list == []:
                self.clients_list.append(newClient)
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
                global transitioning_client
                while transitioning_client != None:
                    time.sleep(1)
                transitioning_client = current_client

class TCPServer:
    def __init__(self):
        logging.info("Initializing TCP Broker")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Welcoming socket for TCP
        self.sock.bind((HOST_IP, TCP_PORT))
        self.sock.listen()
        self.clients_list = []

        while True:
            global transitioning_client
            while transitioning_client == None:
                time.sleep(1)

            current_client = transitioning_client
            connection, client_address = self.sock.accept()
            current_client.client_connection = connection
            current_client.client_address = client_address

            # Add client to list of clients
            self.clients_list.append(current_client)
            transitioning_client = None
            start_new_thread(self.handle_client, (current_client, ))

    def handle_client(self, current_client):
        while True:
            try:
                data = current_client.client_connection.recv(1024)
                # logging.info(f"[TCP] {data}")
                fernet = Fernet(current_client.ciphering_key)
                data = str(fernet.decrypt(data), 'utf-8')
                logging.info(f"[TCP] {data}")
                if data[0:7] == "CONNECT":
                    if current_client.rand == data[8:-1]:
                        send_connected(current_client, fernet)
                    else:
                        logging.info('Client %s cannot be connected. Rand_Cookie invalid!', current_client.client_address)

                elif data[0:12] == "CHAT_REQUEST":
                    client_id = data[13:-1]
                    client_a = current_client
                    client_b = None
                    for requested_client in self.clients_list:
                        if client_id == requested_client.client_id:
                            client_b = requested_client
                            break
                    if client_b != None and client_b.sessionID == None:
                        sessionID = algorithms.create_sessionID()
                        client_a.sessionID = sessionID
                        client_b.sessionID = sessionID
                        send_chat_started(sessionID, client_a, client_b)
                        send_chat_started(sessionID, client_b, client_a)
                    else:
                        send_unreachable(client_a, client_id)

                elif data[0:4] == "CHAT":
                    data = data.split(",")
                    sessionID = data[0][5:]
                    message = data[1][:-1]
                    client_a = current_client
                    client_b = None
                    for requested_client in self.clients_list:
                        if client_a.client_id != requested_client.client_id and requested_client.sessionID == sessionID:
                            client_b = requested_client
                            break
                    if client_b != None:
                        send_chat(client_a, client_b, message)
                        # History needs to happen Here
                        print("chat_history.write_log()")

                elif data[0:11] == "END_REQUEST":
                    sessionID = data[12:-1]
                    client_a = current_client
                    client_b = None
                    for requested_client in self.clients_list:
                        if client_a.client_id != requested_client.client_id and sessionID == requested_client.sessionID:
                            client_b = requested_client
                            break
                    if client_b != None:
                        current_client.sessionID = None
                        self.clients_list[self.clients_list.index(client_b)].sessionID = None
                        send_endnotif(client_b)

                elif data[0:11] == "HISTORY_REQ":
                    # print(MESSAGE)
                    chat_history.read_log("abcd", "efgh")
            except ConnectionResetError:
                for i, any_client in enumerate(self.clients_list):
                    if any_client.client_id == current_client.client_id:
                        self.clients_list.pop(i)
                        break

def main():

    logging.getLogger().setLevel(logging.DEBUG)
    UDPHandler = threading.Thread(target=UDPServer)
    TCPHandler = threading.Thread(target=TCPServer)

    UDPHandler.start()
    TCPHandler.start()

main()
