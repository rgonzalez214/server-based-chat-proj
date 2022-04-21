import socket
import string
import datetime
import random
import secrets
#import chat_history
import threading
x = datetime.datetime.now()

HOST_IP = "127.0.0.1"
PORT = 8009


sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((HOST_IP, PORT))

def connect(MESSAGE):
    print(MESSAGE)

#def chat_started(clients, payload):
#    session_ID = 1234   #redefine how this session ID is created
#    curr_time = x.strftime("%x\t\t%I:%M:%S%p")
#    return chat_history.access_log(curr_time, session_ID, clients, payload)
def a3(key, rand):
    k = key
    m = random.getrandbits(128)
    kb = bin(k)[6:]
    mb = bin(m)[4:]
    kbl = kb[0:64]
    kbr = kb[64:]
    mbl = mb[0:64]
    mbr = mb[64:]
    a1 = int(kbl, 2)
    int(mbr, 2)
    a2 = int(kbr, 2)
    int(mbl, 2)
    a3 = a1 ^ a2
    a4 = bin(a3)[2:].zfill(64)
    a5 = a4[0:32]
    a6 = a4[32:]
    a7 = int(a5, 2)
    int(a6, 2)

def K_Agen():
    i = 0
    while i < 10:
        n = random.getrandbits(128)
        n = n + "\n"
        f1 = open("server/sK_A.txt", "a")
        f2 = open("client/cK_A.txt", "a")
        f1.write(n)
        f2.write(n)
        i += 1

def rand_num():
    nums = string.digits
    nu = ''.join(random.choice(nums) for i in range(10))
    print(nu)
    K_Agen()
    challenge(nu)


def challenge(rand):
    sock.sendto(bytes(rand, "utf-8"), ((HOST_IP, PORT)))


print("[STARTING] server is starting...")
#start()
while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message: %s" % data)
    if "HELLO(" in str(data.decode('utf-8')):
        rand_num()

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

