import socket
import chat_history
import datetime
x = datetime.datetime.now()

HOST_IP = "127.0.0.1"
PORT = 8008

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((HOST_IP, PORT))


def challenge():
    pass


def authenticate():
    pass


def connected():
    pass


def unavailable():
    pass


def end_notif():
    pass

# Function to parse client messages based on message sent by a certain client.
def parse(MESSAGE, client_available=None):
    if MESSAGE[0:5] == "HELLO(":
        challenge()
    if MESSAGE[0:8] == "RESPONSE(":
        authenticate()
    if MESSAGE[0:7] == "CONNECT(":
        connected()
    # S:Think if to include Client A connected messaged should be parsed through this or not
    if MESSAGE[0:12] == "CHAT_REQUEST(":
        if client_available:
            chat_started()
        elif not client_available:
            unavailable()
    if MESSAGE[0:11] == "END_REQUEST(":
        end_notif()
    if MESSAGE[0:4] == "CHAT(":
        print("chat_history.write_log()")
    if MESSAGE[0:11] == "HISTORY_REQ(":
        chat_history.read_log("abcd", "efgh")

# after chat is started between client A and client B
def chat_started(clients, payload):
    session_ID = 1234  # redefine how this session ID is created
    curr_time = x.strftime("%x\t\t%I:%M:%S%p")
    return chat_history.access_log(curr_time, session_ID, clients, payload)


while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("SERVER-received message: %s" % data)
    #  sliced message to separate ID
    client_A_ID = str(data[:9], 'utf-8')

    # update client_B_ID--------------------------------
    client_B_ID = 'client789'
    print("client-A-ID is: ", client_A_ID)
    print("client-B-ID is: ", client_B_ID)

    #  sliced message to separate payload
    payload = str(data[9:], 'utf-8')
    print("payload is: ", payload)
    if payload[:7].lower().strip() == 'history':
        print(payload[7:].lower().strip())
        chat_history.read_log(client_A_ID, payload[7:].lower().strip())

    #  sliced message to separate payload
    if payload[:6].lower() == 'log on':
        print("initiate log on")
        connect("CONNECTED")
    clients= [client_A_ID, client_B_ID]
    res = chat_started(clients, payload)
    print(res)



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
