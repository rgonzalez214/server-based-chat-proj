import socket
import random
import secrets
import chat_history
HOST_IP = "127.0.0.1"
UDP_PORT = 8008
TCP_PORT = 4761

UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Welcoming socket for UDP

def encryptionAlgorithm(key, rand):
    k = key
    m = int(rand,16)
    kb = bin(k)[6:]
    mb = bin(m)[4:]
    kbl = kb[0:64]
    kbr = kb[64:]
    mbl = mb[0:64]
    mbr = mb[64:]
    a1 = int(kbl, 2)^int(mbr, 2)
    a2 = int(kbr, 2)^int(mbl, 2)
    a3 = a1^a2
    a4 = bin(a3)[2:].zfill(64)
    a5 = a4[0:32]
    a6 = a4[32:]
    a7 = int(a5, 2)
    int(a6, 2)
    return bin(a7)[2:].zfill(len(a5))

def rand_num():
    nums = secrets.token_hex(16)
    return nums

def getID(data):
    id = data[data.find('(')+1:data.find(')')]
    return id

def findK(ID):
    f1 = open("listofsubscribers.txt","r")
    clients = f1.readlines()
    found = 0
    for clientInfo in clients:
        if ID in clientInfo:
            found = 1
            key = clientInfo
            key = clientInfo[11:-1]
            return int(key,16)
        found = 0
    f1.close()
    if found == 0:
        print("Could not find Key associated to client!!")

def challenge(rand, clientAddr, clientID):
    global UDPsocket
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
        UDPsocket.sendto(bytes(f"CHALLENGE({rand})", "utf-8"), clientAddr)
        return rand
    else:
        UDPsocket.sendto(bytes("Err:UnverifiedUser", 'utf-8'), clientAddr)

def auth_success(rand_cookie, portnumber, clientAddr):
    UDPsocket.sendto(bytes(f"AUTH_SUCCESS({rand_cookie},{TCP_PORT})", "utf-8"), clientAddr)

def auth_fail(clientAddr):
    UDPsocket.sendto(bytes(f"AUTH_FAIL", "utf-8"), clientAddr)

def connected():
    pass

def chat_started():
    pass

def unavailable():
    pass

def end_notif():
    pass

# Function to parse client messages based on message sent by a certain client.
def parse(MESSAGE, clientAddr):

    if MESSAGE[0:5] == "HELLO":
        rand = challenge(rand_num(), clientAddr, MESSAGE[6:-1])
        response, clientAddr = UDPsocket.recvfrom(1024)  # buffer size is 1024 bytes
        if str(response[0:8],'utf-8') == "RESPONSE":
            ID = str(response[9:19],'utf-8')
            Res = str(response[20:-1],'utf-8')
            XRES = encryptionAlgorithm(findK(ID), rand)
            if Res == XRES:
                auth_success(rand_num(), TCP_PORT, clientAddr)
            else:
                auth_fail(clientAddr)

    if MESSAGE[0:7] == "CONNECT":
        print(MESSAGE)
        connected()

    # S:Think if to include Client A connected messaged should be parsed through this or not
    if MESSAGE[0:12] == "CHAT_REQUEST":
        if client_available:
            print(MESSAGE)
            chat_started()
        elif not client_available:
            print(MESSAGE)
            unavailable()

    if MESSAGE[0:11] == "END_REQUEST":
        print(MESSAGE)
        end_notif()

    if MESSAGE[0:4] == "CHAT":
        print(MESSAGE)
        print("chat_history.write_log()")

    if MESSAGE[0:11] == "HISTORY_REQ":
        print(MESSAGE)
        chat_history.read_log("abcd", "efgh")

def main():
    global UDPsocket
    print("[STARTING] server is starting...")
    UDPsocket.bind((HOST_IP, UDP_PORT)) # UDP socket bound
    print(f"[STARTING] server is running on {HOST_IP}:{UDP_PORT}")

    while True:
        message, addr = UDPsocket.recvfrom(1024) # buffer size is 1024 bytes
        print("SERVER-received message: %s" % message)
        parse(str(message, 'utf-8'), addr)
        #
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
